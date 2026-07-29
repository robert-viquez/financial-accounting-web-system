from django.db import models


class ConfiguracionEmpresa(models.Model):
    nombre = models.CharField(max_length=200, blank=True, default="")
    identificacion = models.CharField(max_length=50, blank=True, default="")
    telefono = models.CharField(max_length=30, blank=True, default="")
    correo = models.EmailField(blank=True, default="")
    direccion = models.TextField(blank=True, default="")
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=13)
    moneda = models.CharField(
        max_length=3,
        choices=[("CRC", "Colón costarricense"), ("USD", "Dólar estadounidense")],
        default="CRC",
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de empresa"

    def __str__(self):
        return self.nombre or "Configuración de empresa"


class RegistroAuditoria(models.Model):
    usuario = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    fecha = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=10)
    ruta = models.CharField(max_length=255)
    codigo_respuesta = models.PositiveSmallIntegerField()
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Registro de auditoría"

    def __str__(self):
        return f"{self.fecha} {self.metodo} {self.ruta}"
