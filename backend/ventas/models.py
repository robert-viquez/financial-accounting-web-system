from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from terceros.models import Cliente, MedioPago
from inventario.models import Producto, MovimientoInventario


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

    def recalcular_totales(self):
        detalles = self.detalles.all()
        self.subtotal = sum(detalle.subtotal for detalle in detalles)
        self.impuesto = Decimal("0.00")
        self.total = self.subtotal - self.descuento + self.impuesto
        self.save(update_fields=["subtotal", "impuesto", "total"])

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

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")

        if self.precio_unitario < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

        if self.descuento < 0:
            raise ValidationError("El descuento no puede ser negativo.")

        if not self.pk and self.producto.stock_actual < self.cantidad:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {self.producto.stock_actual}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento

        es_nuevo = self.pk is None

        super().save(*args, **kwargs)

        if es_nuevo and not self.inventario_descontado:
            self.producto.stock_actual -= self.cantidad
            self.producto.save(update_fields=["stock_actual"])

            MovimientoInventario.objects.create(
                producto=self.producto,
                tipo="SALIDA",
                cantidad=self.cantidad,
                costo_unitario=self.producto.costo_promedio,
                descripcion=f"Salida por venta {self.venta.numero_comprobante}",
            )

            self.inventario_descontado = True
            super().save(update_fields=["inventario_descontado"])

        self.venta.recalcular_totales()

    def delete(self, *args, **kwargs):
        if self.inventario_descontado:
            self.producto.stock_actual += self.cantidad
            self.producto.save(update_fields=["stock_actual"])

            MovimientoInventario.objects.create(
                producto=self.producto,
                tipo="AJUSTE",
                cantidad=self.cantidad,
                costo_unitario=self.producto.costo_promedio,
                descripcion=f"Reversión de venta {self.venta.numero_comprobante}",
            )

        venta = self.venta
        super().delete(*args, **kwargs)
        venta.recalcular_totales()

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"