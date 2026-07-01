from django.db import models

# Create your models here.
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    UNIDAD_MEDIDA = [
        ("KG", "Kilogramo"),
        ("UND", "Unidad"),
        ("PAQ", "Paquete"),
    ]

    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name="productos"
    )
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_MEDIDA, default="KG")
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

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} - {self.cantidad}"