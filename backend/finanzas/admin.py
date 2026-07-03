from django.contrib import admin

from .models import CuentaPorCobrar, PagoCliente, CuentaPorPagar, PagoProveedor


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

class PagoProveedorInline(admin.TabularInline):
    model = PagoProveedor
    extra = 0
    readonly_fields = ("fecha",)


@admin.register(CuentaPorPagar)
class CuentaPorPagarAdmin(admin.ModelAdmin):
    list_display = (
        "compra",
        "proveedor",
        "fecha_emision",
        "fecha_vencimiento",
        "monto_original",
        "saldo",
        "estado",
    )
    list_filter = ("estado", "fecha_vencimiento")
    search_fields = ("compra__numero_factura", "proveedor__nombre")
    inlines = [PagoProveedorInline]


@admin.register(PagoProveedor)
class PagoProveedorAdmin(admin.ModelAdmin):
    list_display = (
        "cuenta_por_pagar",
        "medio_pago",
        "fecha",
        "monto",
        "referencia",
    )
    list_filter = ("medio_pago", "fecha")
    search_fields = (
        "cuenta_por_pagar__compra__numero_factura",
        "cuenta_por_pagar__proveedor__nombre",
        "referencia",
    )