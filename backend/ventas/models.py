from django.contrib.auth.models import User
from django.db import models

from terceros.models import Cliente, MedioPago
from inventario.models import Producto


class Venta(models.Model):
    TIPO_VENTA = [
        ("CONTADO", "Contado"),
        ("CREDITO", "Crédito"),
    ]

    ESTADO = [
        ("EMITIDA", "Emitida"),
        ("ANULADA", "Anulada"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT)
    numero_comprobante = models.CharField(max_length=50, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA, default="CONTADO")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO, default="EMITIDA")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha"]

    def recalcular_totales(self):
        from .services import VentaService

        VentaService.recalcular_totales_venta(self)

    def __str__(self):
        return self.numero_comprobante


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    inventario_descontado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def clean(self):
        from .services import VentaService

        VentaService.validar_detalle_venta(self)

    def save(self, *args, **kwargs):
        from .services import VentaService

        self.subtotal = VentaService.calcular_subtotal_detalle(self)
        self.full_clean()

        es_nuevo = self.pk is None

        super().save(*args, **kwargs)

        if es_nuevo and not self.inventario_descontado:
            VentaService.descontar_inventario_por_venta(self)
            self.inventario_descontado = True
            super().save(update_fields=["inventario_descontado"])

        VentaService.recalcular_totales_venta(self.venta)

    def delete(self, *args, **kwargs):
        from .services import VentaService

        venta = self.venta

        if self.inventario_descontado:
            VentaService.revertir_inventario_por_venta(self)

        super().delete(*args, **kwargs)
        VentaService.recalcular_totales_venta(venta)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"