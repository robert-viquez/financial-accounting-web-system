from django.contrib import admin
from .models import CuentaContable
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