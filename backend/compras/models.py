from django.contrib.auth.models import User
from django.db import models

from terceros.models import Proveedor
from inventario.models import Producto


class Compra(models.Model):
    TIPO_COMPRA = [
        ("CONTADO", "Contado"),
        ("CREDITO", "Crédito"),
    ]

    ESTADO = [
        ("REGISTRADA", "Registrada"),
        ("ANULADA", "Anulada"),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_compra = models.CharField(max_length=20, choices=TIPO_COMPRA, default="CONTADO")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO, default="REGISTRADA")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha"]

    def recalcular_totales(self):
        from .services import CompraService

        CompraService.recalcular_totales_compra(self)

    def __str__(self):
        return self.numero_factura


class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    inventario_actualizado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"

    def clean(self):
        from .services import CompraService

        CompraService.validar_detalle_compra(self)

    def save(self, *args, **kwargs):
        from .services import CompraService

        self.subtotal = CompraService.calcular_subtotal_detalle(self)
        self.full_clean()

        es_nuevo = self.pk is None

        super().save(*args, **kwargs)

        if es_nuevo and not self.inventario_actualizado:
            CompraService.actualizar_inventario_por_compra(self)
            self.inventario_actualizado = True
            super().save(update_fields=["inventario_actualizado"])

        CompraService.recalcular_totales_compra(self.compra)

    def delete(self, *args, **kwargs):
        from .services import CompraService

        compra = self.compra

        if self.inventario_actualizado:
            CompraService.revertir_inventario_por_compra(self)

        super().delete(*args, **kwargs)
        CompraService.recalcular_totales_compra(compra)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"