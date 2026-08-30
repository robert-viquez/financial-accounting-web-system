from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from terceros.models import Cliente, MedioPago
from inventario.models import Producto


class Venta(models.Model):
    TIPO_VENTA = [
        ("CONTADO", "Contado"),
        ("CREDITO", "Crédito"),
    ]

    ESTADO = [
        ("EMITIDA", "Emitida"),
        ("ANULADA", "Anulada"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT)
    numero_comprobante = models.CharField(max_length=50, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA, default="CONTADO")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO, default="EMITIDA")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha"]

    def recalcular_totales(self):
        from .services import VentaService

        VentaService.recalcular_totales_venta(self)

    def __str__(self):
        return self.numero_comprobante


class SecuenciaComprobanteVenta(models.Model):
    """Contador transaccional para emitir comprobantes de venta únicos."""

    periodo = models.CharField(max_length=8, unique=True)
    ultimo_numero = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Secuencia de comprobante de venta"
        verbose_name_plural = "Secuencias de comprobantes de venta"


class ComprobanteElectronico(models.Model):
    """Preparación persistente para una futura integración con Hacienda.

    Este documento permanece desacoplado del comprobante interno y del flujo de
    ventas. En el alcance actual no genera XML fiscal, no firma y no transmite.
    """

    class TipoComprobante(models.TextChoices):
        FACTURA_ELECTRONICA = "FACTURA_ELECTRONICA", "Factura electrónica"
        TIQUETE_ELECTRONICO = "TIQUETE_ELECTRONICO", "Tiquete electrónico"
        NOTA_CREDITO = "NOTA_CREDITO", "Nota de crédito"
        NOTA_DEBITO = "NOTA_DEBITO", "Nota de débito"

    class EstadoHacienda(models.TextChoices):
        # BORRADOR significa preparado internamente, aún no enviado a Hacienda.
        BORRADOR = "BORRADOR", "Borrador"
        PENDIENTE = "PENDIENTE", "Pendiente"
        ENVIADO = "ENVIADO", "Enviado"
        ACEPTADO = "ACEPTADO", "Aceptado"
        RECHAZADO = "RECHAZADO", "Rechazado"
        ERROR = "ERROR", "Error"

    venta = models.ForeignKey(
        Venta,
        on_delete=models.PROTECT,
        related_name="comprobantes_electronicos",
    )
    clave_numerica = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{50}$",
                message="La clave numérica debe contener exactamente 50 dígitos.",
            )
        ],
    )
    # Es independiente de Venta.numero_comprobante y su secuencia interna.
    consecutivo = models.CharField(max_length=20, unique=True, null=True, blank=True)
    tipo_comprobante = models.CharField(max_length=24, choices=TipoComprobante.choices)
    xml_generado = models.TextField(null=True, blank=True)
    estado_hacienda = models.CharField(
        max_length=12,
        choices=EstadoHacienda.choices,
        default=EstadoHacienda.BORRADOR,
    )
    mensaje_hacienda = models.TextField(null=True, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_creado = models.DateTimeField(auto_now_add=True)
    fecha_actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comprobante electrónico"
        verbose_name_plural = "Comprobantes electrónicos"
        ordering = ["-fecha_creado"]
        indexes = [
            models.Index(fields=["estado_hacienda"]),
            models.Index(fields=["tipo_comprobante"]),
            models.Index(fields=["fecha_envio"]),
        ]

    def clean(self):
        super().clean()
        if (
            self.fecha_envio
            and self.fecha_respuesta
            and self.fecha_respuesta < self.fecha_envio
        ):
            raise ValidationError(
                {"fecha_respuesta": "La fecha de respuesta no puede ser anterior a la fecha de envío."}
            )

    def __str__(self):
        return f"{self.get_tipo_comprobante_display()} - {self.venta.numero_comprobante}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    inventario_descontado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def clean(self):
        from .services import VentaService

        VentaService.validar_detalle_venta(self)

    def save(self, *args, **kwargs):
        from .services import VentaService
        from inventario.quantities import normalize_quantity

        # Normalize before calculating the subtotal and before the same instance
        # is passed to inventory. MySQL otherwise persists three decimals while
        # Python continues carrying the unrounded amount-derived quantity.
        self.cantidad = normalize_quantity(self.cantidad)
        self.subtotal = VentaService.calcular_subtotal_detalle(self)
        self.full_clean()

        es_nuevo = self.pk is None

        super().save(*args, **kwargs)

        if es_nuevo and not self.inventario_descontado:
            VentaService.descontar_inventario_por_venta(self)
            self.inventario_descontado = True
            super().save(update_fields=["inventario_descontado"])

        VentaService.finalizar_venta(self.venta)

    def delete(self, *args, **kwargs):
        from .services import VentaService

        venta = self.venta

        if self.inventario_descontado:
            VentaService.revertir_inventario_por_venta(self)

        super().delete(*args, **kwargs)
        VentaService.recalcular_totales_venta(venta)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"
