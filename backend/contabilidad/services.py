from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import AsientoContable, CuentaContable, DetalleAsiento, PeriodoContable


CUENTAS_BASE = {
    "1101": ("Caja y bancos", "ACTIVO", "DEUDORA"),
    "1102": ("Cuentas por cobrar", "ACTIVO", "DEUDORA"),
    "1201": ("Inventario", "ACTIVO", "DEUDORA"),
    "2101": ("Cuentas por pagar", "PASIVO", "ACREEDORA"),
    "3101": ("Patrimonio", "PATRIMONIO", "ACREEDORA"),
    "4101": ("Ventas", "INGRESO", "ACREEDORA"),
    "5101": ("Costo de ventas", "COSTO", "DEUDORA"),
}


class ContabilidadService:
    @staticmethod
    def asegurar_catalogo_base():
        cuentas = {}
        for codigo, (nombre, tipo, naturaleza) in CUENTAS_BASE.items():
            cuenta, _ = CuentaContable.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "tipo": tipo,
                    "naturaleza": naturaleza,
                    "nivel": 1,
                    "permite_movimientos": True,
                },
            )
            cuentas[codigo] = cuenta
        return cuentas

    @staticmethod
    def validar_periodo_abierto(fecha):
        periodo = PeriodoContable.objects.filter(
            fecha_inicio__lte=fecha,
            fecha_fin__gte=fecha,
        ).first()
        if periodo and periodo.cerrado:
            raise ValidationError("El periodo contable de la fecha está cerrado.")

    @staticmethod
    def siguiente_numero():
        year = timezone.localdate().year
        ultimo = (
            AsientoContable.objects.filter(numero__startswith=f"ASI-{year}-")
            .aggregate(valor=Max("numero"))["valor"]
        )
        consecutivo = int(ultimo.rsplit("-", 1)[-1]) + 1 if ultimo else 1
        return f"ASI-{year}-{consecutivo:06d}"

    @staticmethod
    @transaction.atomic
    def guardar_asiento(
        *,
        fecha,
        descripcion,
        usuario,
        lineas,
        origen="MANUAL",
        referencia="",
        contabilizar=True,
        monto_transaccion=None,
    ):
        ContabilidadService.validar_periodo_abierto(fecha)
        for linea in lineas:
            linea["debe"] = Decimal(str(linea.get("debe", 0))).quantize(Decimal("0.01"))
            linea["haber"] = Decimal(str(linea.get("haber", 0))).quantize(Decimal("0.01"))
        total_debe = sum((linea["debe"] for linea in lineas), Decimal("0"))
        total_haber = sum((linea["haber"] for linea in lineas), Decimal("0"))
        if not lineas or total_debe <= 0 or total_debe != total_haber:
            raise ValidationError("El asiento debe estar balanceado y ser mayor a cero.")
        movimientos = {}
        for linea in lineas:
            tipo = linea.get("tipo_movimiento", "GENERAL")
            subtotal = movimientos.setdefault(tipo, {"debe": Decimal("0"), "haber": Decimal("0")})
            subtotal["debe"] += linea["debe"]
            subtotal["haber"] += linea["haber"]
        if any(valores["debe"] <= 0 or valores["debe"] != valores["haber"] for valores in movimientos.values()):
            raise ValidationError("Cada movimiento contable debe estar balanceado y ser mayor a cero.")

        asiento = None
        if referencia:
            asiento = AsientoContable.objects.filter(
                origen=origen,
                referencia=referencia or None,
            ).first()
        if asiento and asiento.estado == "ANULADO":
            raise ValidationError("No se puede modificar un asiento anulado.")
        if asiento:
            asiento.detalles.all().delete()
            asiento.fecha = fecha
            asiento.descripcion = descripcion
            asiento.usuario = usuario
            asiento.monto_transaccion = monto_transaccion
        else:
            asiento = AsientoContable(
                numero=ContabilidadService.siguiente_numero(),
                fecha=fecha,
                descripcion=descripcion,
                usuario=usuario,
                origen=origen,
                referencia=referencia,
                monto_transaccion=monto_transaccion,
            )

        asiento.estado = "CONTABILIZADO" if contabilizar else "BORRADOR"
        asiento.contabilizado_en = timezone.now() if contabilizar else None
        asiento.save()
        for linea in lineas:
            detalle = DetalleAsiento(
                asiento=asiento,
                cuenta=linea["cuenta"],
                descripcion=linea.get("descripcion", ""),
                tipo_movimiento=linea.get("tipo_movimiento", "GENERAL"),
                debe=Decimal(str(linea.get("debe", 0))),
                haber=Decimal(str(linea.get("haber", 0))),
            )
            detalle.full_clean()
            detalle.save()
        return asiento

    @staticmethod
    @transaction.atomic
    def anular_por_origen(origen, referencia):
        asiento = AsientoContable.objects.filter(
            origen=origen,
            referencia=str(referencia),
        ).first()
        if asiento and asiento.estado != "ANULADO":
            ContabilidadService.validar_periodo_abierto(asiento.fecha)
            asiento.estado = "ANULADO"
            asiento.save(update_fields=["estado"])
        return asiento

    @staticmethod
    def contabilizar_venta(venta):
        cuentas = ContabilidadService.asegurar_catalogo_base()
        contrapartida = cuentas["1102"] if venta.tipo_venta == "CREDITO" else cuentas["1101"]
        costo = sum(
            (
                detalle.cantidad * detalle.producto.costo_promedio
                for detalle in venta.detalles.select_related("producto")
            ),
            Decimal("0.00"),
        )
        lineas = [
            {"cuenta": contrapartida, "debe": venta.total, "haber": 0, "tipo_movimiento": "VENTA"},
            {"cuenta": cuentas["4101"], "debe": 0, "haber": venta.total, "tipo_movimiento": "VENTA"},
        ]
        if costo > 0:
            lineas.extend([
                {"cuenta": cuentas["5101"], "debe": costo, "haber": 0, "tipo_movimiento": "COSTO_VENTA"},
                {"cuenta": cuentas["1201"], "debe": 0, "haber": costo, "tipo_movimiento": "COSTO_VENTA"},
            ])
        return ContabilidadService.guardar_asiento(
            fecha=timezone.localtime(venta.fecha).date(),
            descripcion=f"Venta {venta.numero_comprobante}",
            usuario=venta.usuario,
            lineas=lineas,
            origen="VENTA",
            referencia=str(venta.pk),
            monto_transaccion=venta.total,
        )

    @staticmethod
    def contabilizar_compra(compra):
        cuentas = ContabilidadService.asegurar_catalogo_base()
        contrapartida = cuentas["2101"] if compra.tipo_compra == "CREDITO" else cuentas["1101"]
        return ContabilidadService.guardar_asiento(
            fecha=timezone.localtime(compra.fecha).date(),
            descripcion=f"Compra {compra.numero_factura}",
            usuario=compra.usuario,
            lineas=[
                {"cuenta": cuentas["1201"], "debe": compra.total, "haber": 0, "tipo_movimiento": "COMPRA"},
                {"cuenta": contrapartida, "debe": 0, "haber": compra.total, "tipo_movimiento": "COMPRA"},
            ],
            origen="COMPRA",
            referencia=str(compra.pk),
            monto_transaccion=compra.total,
        )

    @staticmethod
    def contabilizar_cobro(pago):
        cuentas = ContabilidadService.asegurar_catalogo_base()
        return ContabilidadService.guardar_asiento(
            fecha=timezone.localtime(pago.fecha).date(),
            descripcion=f"Cobro de {pago.cuenta_por_cobrar.cliente.nombre}",
            usuario=pago.usuario or pago.cuenta_por_cobrar.venta.usuario,
            lineas=[
                {"cuenta": cuentas["1101"], "debe": pago.monto, "haber": 0, "tipo_movimiento": "COBRO"},
                {"cuenta": cuentas["1102"], "debe": 0, "haber": pago.monto, "tipo_movimiento": "COBRO"},
            ],
            origen="COBRO",
            referencia=str(pago.pk),
            monto_transaccion=pago.monto,
        )

    @staticmethod
    def contabilizar_pago(pago):
        cuentas = ContabilidadService.asegurar_catalogo_base()
        return ContabilidadService.guardar_asiento(
            fecha=timezone.localtime(pago.fecha).date(),
            descripcion=f"Pago a {pago.cuenta_por_pagar.proveedor.nombre}",
            usuario=pago.usuario or pago.cuenta_por_pagar.compra.usuario,
            lineas=[
                {"cuenta": cuentas["2101"], "debe": pago.monto, "haber": 0, "tipo_movimiento": "PAGO"},
                {"cuenta": cuentas["1101"], "debe": 0, "haber": pago.monto, "tipo_movimiento": "PAGO"},
            ],
            origen="PAGO",
            referencia=str(pago.pk),
            monto_transaccion=pago.monto,
        )

    @staticmethod
    def reporte_saldos(desde=None, hasta=None):
        detalles = DetalleAsiento.objects.filter(asiento__estado="CONTABILIZADO")
        if desde:
            detalles = detalles.filter(asiento__fecha__gte=desde)
        if hasta:
            detalles = detalles.filter(asiento__fecha__lte=hasta)
        return (
            detalles.values(
                "cuenta_id",
                "cuenta__codigo",
                "cuenta__nombre",
                "cuenta__tipo",
                "cuenta__naturaleza",
            )
            .annotate(
                debe=Coalesce(Sum("debe"), Decimal("0.00")),
                haber=Coalesce(Sum("haber"), Decimal("0.00")),
            )
            .order_by("cuenta__codigo")
        )
