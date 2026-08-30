from django.contrib import admin
from .models import ComprobanteElectronico, Venta, DetalleVenta


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


@admin.register(ComprobanteElectronico)
class ComprobanteElectronicoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "venta", "tipo_comprobante", "consecutivo",
        "estado_hacienda", "fecha_envio", "fecha_respuesta",
    )
    search_fields = ("venta__numero_comprobante", "clave_numerica", "consecutivo")
    list_filter = ("tipo_comprobante", "estado_hacienda")
    readonly_fields = (
        "clave_numerica", "consecutivo", "xml_generado", "estado_hacienda",
        "mensaje_hacienda", "fecha_envio", "fecha_respuesta", "fecha_creado",
        "fecha_actualizado",
    )
