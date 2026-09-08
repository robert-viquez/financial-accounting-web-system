from django.contrib import admin
from .models import ConfiguracionEmpresa, PreferenciaUsuario, RegistroAuditoria


admin.site.register(ConfiguracionEmpresa)
admin.site.register(PreferenciaUsuario)
admin.site.register(RegistroAuditoria)
