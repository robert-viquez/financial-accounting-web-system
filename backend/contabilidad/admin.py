from django.contrib import admin
from .models import AsientoContable, CuentaContable, DetalleAsiento, PeriodoContable
# Register your models here.

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "tipo",
        "naturaleza",
        "nivel",
        "cuenta_padre",
        "permite_movimientos",
        "estado",
    )
    list_filter = ("tipo", "naturaleza", "estado")
    search_fields = ("codigo", "nombre")
    ordering = ("codigo",)


class DetalleAsientoInline(admin.TabularInline):
    model = DetalleAsiento
    extra = 0


@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ("numero", "fecha", "descripcion", "origen", "estado", "usuario")
    list_filter = ("estado", "origen", "fecha")
    search_fields = ("numero", "descripcion", "referencia")
    inlines = [DetalleAsientoInline]


admin.site.register(PeriodoContable)
