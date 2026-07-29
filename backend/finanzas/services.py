from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import CuentaPorCobrar, CuentaPorPagar


class FinanzasService:
    @staticmethod
    @transaction.atomic
    def crear_cuenta_por_cobrar_desde_venta(venta, dias_credito=None):
        if venta.tipo_venta != "CREDITO":
            return None

        if not venta.cliente:
            raise ValidationError("Una venta a crédito debe tener cliente.")

        dias_credito = venta.cliente.dias_credito if dias_credito is None else dias_credito
        cuenta, creada = CuentaPorCobrar.objects.get_or_create(
            venta=venta,
            defaults={
                "cliente": venta.cliente,
                "fecha_vencimiento": timezone.now().date() + timedelta(days=dias_credito),
                "monto_original": venta.total,
                "saldo": venta.total,
                "estado": "PENDIENTE",
            },
        )
        if not creada and not cuenta.pagos.exists():
            cuenta.cliente = venta.cliente
            cuenta.monto_original = venta.total
            cuenta.saldo = venta.total
            cuenta.estado = "PENDIENTE"
            cuenta.save(update_fields=["cliente", "monto_original", "saldo", "estado"])

        return cuenta

    @staticmethod
    @transaction.atomic
    def crear_cuenta_por_pagar_desde_compra(compra, dias_credito=None):
        if compra.tipo_compra != "CREDITO":
            return None

        dias_credito = compra.proveedor.dias_credito if dias_credito is None else dias_credito
        cuenta, creada = CuentaPorPagar.objects.get_or_create(
            compra=compra,
            defaults={
                "proveedor": compra.proveedor,
                "fecha_vencimiento": timezone.now().date() + timedelta(days=dias_credito),
                "monto_original": compra.total,
                "saldo": compra.total,
                "estado": "PENDIENTE",
            },
        )
        if not creada and not cuenta.pagos.exists():
            cuenta.proveedor = compra.proveedor
            cuenta.monto_original = compra.total
            cuenta.saldo = compra.total
            cuenta.estado = "PENDIENTE"
            cuenta.save(update_fields=["proveedor", "monto_original", "saldo", "estado"])

        return cuenta

    @staticmethod
    def validar_pago_cliente(pago):
        if pago.monto <= 0:
            raise ValidationError("El monto del pago debe ser mayor a cero.")

        if pago.monto > pago.cuenta_por_cobrar.saldo:
            raise ValidationError("El pago no puede ser mayor al saldo pendiente.")

        if pago.cuenta_por_cobrar.estado in ["PAGADA", "ANULADA"]:
            raise ValidationError("No se puede pagar una cuenta pagada o anulada.")

    @staticmethod
    @transaction.atomic
    def aplicar_pago_cliente(pago):
        cuenta = pago.cuenta_por_cobrar

        cuenta.saldo -= pago.monto

        if cuenta.saldo == 0:
            cuenta.estado = "PAGADA"
        elif cuenta.saldo < cuenta.monto_original:
            cuenta.estado = "PARCIAL"

        cuenta.save(update_fields=["saldo", "estado"])

        from contabilidad.services import ContabilidadService
        ContabilidadService.contabilizar_cobro(pago)

    @staticmethod
    def validar_pago_proveedor(pago):
        if pago.monto <= 0:
            raise ValidationError("El monto del pago debe ser mayor a cero.")

        if pago.monto > pago.cuenta_por_pagar.saldo:
            raise ValidationError("El pago no puede ser mayor al saldo pendiente.")

        if pago.cuenta_por_pagar.estado in ["PAGADA", "ANULADA"]:
            raise ValidationError("No se puede pagar una cuenta pagada o anulada.")

    @staticmethod
    @transaction.atomic
    def aplicar_pago_proveedor(pago):
        cuenta = pago.cuenta_por_pagar

        cuenta.saldo -= pago.monto

        if cuenta.saldo == 0:
            cuenta.estado = "PAGADA"
        elif cuenta.saldo < cuenta.monto_original:
            cuenta.estado = "PARCIAL"

        cuenta.save(update_fields=["saldo", "estado"])

        from contabilidad.services import ContabilidadService
        ContabilidadService.contabilizar_pago(pago)

    @staticmethod
    @transaction.atomic
    def anular_pago_cliente(pago):
        from django.utils import timezone
        from contabilidad.services import ContabilidadService

        pago = pago.__class__.objects.select_for_update().get(pk=pago.pk)
        if pago.estado == "ANULADO":
            raise ValidationError("El pago ya está anulado.")
        cuenta = CuentaPorCobrar.objects.select_for_update().get(
            pk=pago.cuenta_por_cobrar_id
        )
        cuenta.saldo += pago.monto
        cuenta.estado = "PENDIENTE" if cuenta.saldo == cuenta.monto_original else "PARCIAL"
        cuenta.save(update_fields=["saldo", "estado"])
        pago.estado = "ANULADO"
        pago.anulado_en = timezone.now()
        pago.__class__.objects.filter(pk=pago.pk).update(
            estado=pago.estado,
            anulado_en=pago.anulado_en,
        )
        ContabilidadService.anular_por_origen("COBRO", pago.pk)
        return pago

    @staticmethod
    @transaction.atomic
    def anular_pago_proveedor(pago):
        from django.utils import timezone
        from contabilidad.services import ContabilidadService

        pago = pago.__class__.objects.select_for_update().get(pk=pago.pk)
        if pago.estado == "ANULADO":
            raise ValidationError("El pago ya está anulado.")
        cuenta = CuentaPorPagar.objects.select_for_update().get(
            pk=pago.cuenta_por_pagar_id
        )
        cuenta.saldo += pago.monto
        cuenta.estado = "PENDIENTE" if cuenta.saldo == cuenta.monto_original else "PARCIAL"
        cuenta.save(update_fields=["saldo", "estado"])
        pago.estado = "ANULADO"
        pago.anulado_en = timezone.now()
        pago.__class__.objects.filter(pk=pago.pk).update(
            estado=pago.estado,
            anulado_en=pago.anulado_en,
        )
        ContabilidadService.anular_por_origen("PAGO", pago.pk)
        return pago
