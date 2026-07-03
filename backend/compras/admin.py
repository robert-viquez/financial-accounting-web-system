from django.contrib import admin

from .models import Compra, DetalleCompra


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        "numero_factura",
        "proveedor",
        "usuario",
        "tipo_compra",
        "subtotal",
        "impuesto",
        "total",
        "estado",
        "fecha",
    )
    list_filter = ("tipo_compra", "estado", "fecha")
    search_fields = ("numero_factura", "proveedor__nombre")
    inlines = [DetalleCompraInline]


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = (
        "compra",
        "producto",
        "cantidad",
        "costo_unitario",
        "subtotal",
        "inventario_actualizado",
    )