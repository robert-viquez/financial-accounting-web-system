from django.db import models

from terceros.models import Cliente, MedioPago
from ventas.models import Venta


class CuentaPorCobrar(models.Model):
    ESTADO = [
        ("PENDIENTE", "Pendiente"),
        ("PARCIAL", "Parcial"),
        ("PAGADA", "Pagada"),
        ("ANULADA", "Anulada"),
    ]

    venta = models.OneToOneField(
        Venta,
        on_delete=models.PROTECT,
        related_name="cuenta_por_cobrar"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="cuentas_por_cobrar"
    )
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    monto_original = models.DecimalField(max_digits=12, decimal_places=2)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO, default="PENDIENTE")

    class Meta:
        verbose_name = "Cuenta por cobrar"
        verbose_name_plural = "Cuentas por cobrar"
        ordering = ["fecha_vencimiento"]

    def __str__(self):
        return f"CxC {self.venta.numero_comprobante} - {self.cliente.nombre}"


class PagoCliente(models.Model):
    cuenta_por_cobrar = models.ForeignKey(
        CuentaPorCobrar,
        on_delete=models.PROTECT,
        related_name="pagos"
    )
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Pago de cliente"
        verbose_name_plural = "Pagos de clientes"
        ordering = ["-fecha"]

    def save(self, *args, **kwargs):
        from .services import FinanzasService

        es_nuevo = self.pk is None
        FinanzasService.validar_pago_cliente(self)

        super().save(*args, **kwargs)

        if es_nuevo:
            FinanzasService.aplicar_pago_cliente(self)

    def __str__(self):
        return f"Pago {self.monto} - {self.cuenta_por_cobrar}"