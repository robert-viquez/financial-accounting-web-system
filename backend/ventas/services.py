from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from inventario.models import MovimientoInventario, Producto

from .models import ComprobanteElectronico, SecuenciaComprobanteVenta

class VentaService:
    @staticmethod
    def generar_numero_comprobante():
        """Genera V-AAAAMMDD-000001 con bloqueo para evitar duplicados."""
        periodo = timezone.localdate().strftime("%Y%m%d")
        secuencia, _ = (
            SecuenciaComprobanteVenta.objects.select_for_update()
            .get_or_create(periodo=periodo)
        )
        secuencia.ultimo_numero += 1
        secuencia.save(update_fields=["ultimo_numero"])
        return f"V-{periodo}-{secuencia.ultimo_numero:06d}"

    @staticmethod
    def validar_detalle_venta(detalle):
        if detalle.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")

        if detalle.precio_unitario < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

        unidad = detalle.producto.unidad_medida
        if unidad and not unidad.permite_decimales and detalle.cantidad != detalle.cantidad.to_integral_value():
            raise ValidationError(f"{detalle.producto.nombre} sólo admite cantidades enteras ({unidad.simbolo}).")

        if detalle.descuento < 0:
            raise ValidationError("El descuento no puede ser negativo.")

        subtotal = (detalle.cantidad * detalle.precio_unitario) - detalle.descuento

        if subtotal < 0:
            raise ValidationError("El subtotal no puede ser negativo.")

        if not detalle.pk and detalle.producto.stock_actual < detalle.cantidad:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {detalle.producto.stock_actual}"
            )

    @staticmethod
    def calcular_subtotal_detalle(detalle):
        subtotal = (detalle.cantidad * detalle.precio_unitario) - detalle.descuento
        return subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def recalcular_totales_venta(venta):
        detalles = venta.detalles.all()
        venta.subtotal = sum((detalle.subtotal for detalle in detalles), Decimal("0.00"))
        venta.impuesto = Decimal("0.00")
        venta.total = (venta.subtotal - venta.descuento + venta.impuesto).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
        venta.save(update_fields=["subtotal", "impuesto", "total"])

    @staticmethod
    def finalizar_venta(venta):
        VentaService.recalcular_totales_venta(venta)

        if venta.tipo_venta == "CREDITO":
            from finanzas.services import FinanzasService

            FinanzasService.crear_cuenta_por_cobrar_desde_venta(venta)

        from contabilidad.services import ContabilidadService
        ContabilidadService.contabilizar_venta(venta)
            
    @staticmethod
    @transaction.atomic
    def descontar_inventario_por_venta(detalle):
        producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)

        if producto.stock_actual < detalle.cantidad:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {producto.stock_actual}"
            )

        producto.stock_actual -= detalle.cantidad
        producto.save(update_fields=["stock_actual"])

        MovimientoInventario.objects.create(
            producto=producto,
            tipo="SALIDA",
            cantidad=detalle.cantidad,
            costo_unitario=producto.costo_promedio,
            descripcion=f"Salida por venta {detalle.venta.numero_comprobante}",
            usuario=detalle.venta.usuario,
        )

    @staticmethod
    @transaction.atomic
    def revertir_inventario_por_venta(detalle):
        producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)

        producto.stock_actual += detalle.cantidad
        producto.save(update_fields=["stock_actual"])

        MovimientoInventario.objects.create(
            producto=producto,
            tipo="AJUSTE",
            cantidad=detalle.cantidad,
            costo_unitario=producto.costo_promedio,
            descripcion=f"Reversión de venta {detalle.venta.numero_comprobante}",
            usuario=detalle.venta.usuario,
        )


class FacturacionElectronicaService:
    """Operaciones internas preparatorias, sin comunicación con Hacienda."""

    @staticmethod
    def validar_datos_preparacion(venta):
        """Informa faltantes fiscales sin impedir el registro normal de ventas."""
        faltantes = []
        if not venta.cliente_id:
            faltantes.append("cliente")
        else:
            if not venta.cliente.nombre:
                faltantes.append("nombre_cliente")
            if not venta.cliente.identificacion:
                faltantes.append("identificacion_cliente")
        if not venta.medio_pago_id:
            faltantes.append("medio_pago")
        detalles = venta.detalles.select_related("producto").all()
        if not detalles.exists():
            faltantes.append("detalles_venta")
        else:
            for detalle in detalles:
                if not detalle.producto.codigo:
                    faltantes.append("codigo_producto")
                    break
        return {"preparado": not faltantes, "faltantes": faltantes}

    @staticmethod
    @transaction.atomic
    def preparar_comprobante(venta, tipo_comprobante):
        """Crea solamente un borrador; no genera datos fiscales ni efectos de venta."""
        comprobante = ComprobanteElectronico(
            venta=venta,
            tipo_comprobante=tipo_comprobante,
            estado_hacienda=ComprobanteElectronico.EstadoHacienda.BORRADOR,
        )
        comprobante.full_clean()
        comprobante.save()
        return comprobante

    @staticmethod
    def obtener_comprobantes(venta):
        return venta.comprobantes_electronicos.all()
