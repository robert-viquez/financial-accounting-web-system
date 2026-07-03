from django.contrib import admin

from .models import CuentaPorCobrar, PagoCliente


class PagoClienteInline(admin.TabularInline):
    model = PagoCliente
    extra = 0
    readonly_fields = ("fecha",)


@admin.register(CuentaPorCobrar)
class CuentaPorCobrarAdmin(admin.ModelAdmin):
    list_display = (
        "venta",
        "cliente",
        "fecha_emision",
        "fecha_vencimiento",
        "monto_original",
        "saldo",
        "estado",
    )
    list_filter = ("estado", "fecha_vencimiento")
    search_fields = ("venta__numero_comprobante", "cliente__nombre")
    inlines = [PagoClienteInline]


@admin.register(PagoCliente)
class PagoClienteAdmin(admin.ModelAdmin):
    list_display = (
        "cuenta_por_cobrar",
        "medio_pago",
        "fecha",
        "monto",
        "referencia",
    )
    list_filter = ("medio_pago", "fecha")
    search_fields = (
        "cuenta_por_cobrar__venta__numero_comprobante",
        "cuenta_por_cobrar__cliente__nombre",
        "referencia",
    )