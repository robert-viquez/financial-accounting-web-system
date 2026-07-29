from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.
class CategoriaProducto(models.Model):
    codigo = models.CharField(max_length=12, unique=True, editable=False)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.codigo:
            base = "".join(
                palabra[0] for palabra in slugify(self.nombre).split("-") if palabra
            ).upper()[:6] or "CAT"
            codigo = base
            consecutivo = 2
            while CategoriaProducto.objects.exclude(pk=self.pk).filter(codigo=codigo).exists():
                codigo = f"{base[:8]}{consecutivo}"
                consecutivo += 1
            self.codigo = codigo
        super().save(*args, **kwargs)


class Producto(models.Model):
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name="productos"
    )
    codigo = models.CharField(max_length=30, unique=True)
    codigo_barras = models.CharField(max_length=64, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.ForeignKey(
        "UnidadMedida",
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
    )
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2)
    costo_promedio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class UnidadMedida(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=60, unique=True)
    simbolo = models.CharField(max_length=12)
    permite_decimales = models.BooleanField(default=True)
    estado = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"


class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
        ("AJUSTE", "Ajuste"),
    ]

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="movimientos"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimientos_inventario",
    )

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} - {self.cantidad}"
