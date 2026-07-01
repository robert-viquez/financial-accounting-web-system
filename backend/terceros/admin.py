from django.contrib import admin
from .models import Cliente, Proveedor, MedioPago
# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "identificacion", "telefono", "correo", "estado")
    search_fields = ("nombre", "identificacion", "telefono", "correo")
    list_filter = ("estado",)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "identificacion", "telefono", "correo", "estado")
    search_fields = ("nombre", "identificacion", "telefono", "correo")
    list_filter = ("estado",)


@admin.register(MedioPago)
class MedioPagoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado")
    search_fields = ("nombre",)
    list_filter = ("estado",)