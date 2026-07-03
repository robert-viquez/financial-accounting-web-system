from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import CuentaPorCobrar


class FinanzasService:
    @staticmethod
    @transaction.atomic
    def crear_cuenta_por_cobrar_desde_venta(venta, dias_credito=30):
        if venta.tipo_venta != "CREDITO":
            return None

        if not venta.cliente:
            raise ValidationError("Una venta a crédito debe tener cliente.")

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