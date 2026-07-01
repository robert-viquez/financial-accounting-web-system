from django.contrib import admin
from .models import CategoriaProducto, Producto, MovimientoInventario
# Register your models here.

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado")
    search_fields = ("nombre",)
    list_filter = ("estado",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "categoria",
        "unidad_medida",
        "precio_venta",
        "costo_promedio",
        "stock_actual",
        "stock_minimo",
        "estado",
    )
    search_fields = ("codigo", "nombre")
    list_filter = ("categoria", "unidad_medida", "estado")


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        "producto",
        "tipo",
        "cantidad",
        "costo_unitario",
        "fecha",
    )
    search_fields = ("producto__nombre", "producto__codigo")
    list_filter = ("tipo", "fecha")