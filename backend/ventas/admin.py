from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        "numero_comprobante",
        "cliente",
        "usuario",
        "medio_pago",
        "tipo_venta",
        "total",
        "estado",
        "fecha",
    )
    list_filter = ("tipo_venta", "estado", "medio_pago", "fecha")
    search_fields = ("numero_comprobante", "cliente__nombre")
    inlines = [DetalleVentaInline]


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = (
        "venta",
        "producto",
        "cantidad",
        "precio_unitario",
        "descuento",
        "subtotal",
    )