from django.db import models

# Create your models here.
class CuentaContable(models.Model):
    TIPO_CUENTA = [
        ("ACTIVO", "Activo"),
        ("PASIVO", "Pasivo"),
        ("PATRIMONIO", "Patrimonio"),
        ("INGRESO", "Ingreso"),
        ("GASTO", "Gasto"),
        ("COSTO", "Costo"),
    ]

    NATURALEZA = [
        ("DEUDORA", "Deudora"),
        ("ACREEDORA", "Acreedora"),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPO_CUENTA)
    naturaleza = models.CharField(max_length=20, choices=NATURALEZA)
    nivel = models.PositiveSmallIntegerField(default=1)
    cuenta_padre = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcuentas"
    )
    permite_movimientos = models.BooleanField(default=True)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cuenta contable"
        verbose_name_plural = "Cuentas contables"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"