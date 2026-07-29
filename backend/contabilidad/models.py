from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

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


class PeriodoContable(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_inicio"]
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_fin__gte=models.F("fecha_inicio")),
                name="periodo_fechas_validas",
            )
        ]

    def clean(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha final debe ser posterior a la inicial.")
        if PeriodoContable.objects.exclude(pk=self.pk).filter(
            fecha_inicio__lte=self.fecha_fin,
            fecha_fin__gte=self.fecha_inicio,
        ).exists():
            raise ValidationError("El periodo se traslapa con otro periodo contable.")

    def __str__(self):
        return self.nombre


class AsientoContable(models.Model):
    ESTADOS = [
        ("BORRADOR", "Borrador"),
        ("CONTABILIZADO", "Contabilizado"),
        ("ANULADO", "Anulado"),
    ]
    ORIGENES = [
        ("MANUAL", "Manual"),
        ("VENTA", "Venta"),
        ("COMPRA", "Compra"),
        ("COBRO", "Cobro"),
        ("PAGO", "Pago"),
    ]

    numero = models.CharField(max_length=30, unique=True)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    origen = models.CharField(max_length=20, choices=ORIGENES, default="MANUAL")
    referencia = models.CharField(max_length=100, blank=True, null=True, default=None)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="BORRADOR")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    creado_en = models.DateTimeField(auto_now_add=True)
    contabilizado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["origen", "referencia"],
                name="asiento_origen_referencia_unica",
            )
        ]

    @property
    def total_debe(self):
        return sum((linea.debe for linea in self.detalles.all()), Decimal("0.00"))

    @property
    def total_haber(self):
        return sum((linea.haber for linea in self.detalles.all()), Decimal("0.00"))

    def __str__(self):
        return f"{self.numero} - {self.descripcion}"


class DetalleAsiento(models.Model):
    asiento = models.ForeignKey(
        AsientoContable,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    cuenta = models.ForeignKey(
        CuentaContable,
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    descripcion = models.CharField(max_length=255, blank=True, default="")
    debe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(debe__gt=0) & Q(haber=0))
                    | (Q(haber__gt=0) & Q(debe=0))
                ),
                name="detalle_solo_debe_o_haber",
            )
        ]

    def clean(self):
        if not self.cuenta.permite_movimientos or not self.cuenta.estado:
            raise ValidationError("La cuenta seleccionada no admite movimientos.")
        if self.debe < 0 or self.haber < 0:
            raise ValidationError("Debe y haber no pueden ser negativos.")
        if (self.debe > 0) == (self.haber > 0):
            raise ValidationError("La línea debe tener un valor en debe o en haber.")

    def __str__(self):
        return f"{self.asiento.numero} - {self.cuenta.codigo}"
