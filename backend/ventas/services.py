from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from inventario.models import MovimientoInventario


class VentaService:
    @staticmethod
    def validar_detalle_venta(detalle):
        if detalle.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")

        if detalle.precio_unitario < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

        if detalle.descuento < 0:
            raise ValidationError("El descuento no puede ser negativo.")

        subtotal = (detalle.cantidad * detalle.precio_unitario) - detalle.descuento

        if subtotal < 0:
            raise ValidationError("El subtotal no puede ser negativo.")

        if not detalle.pk and detalle.producto.stock_actual < detalle.cantidad:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {detalle.producto.stock_actual}"
            )

    @staticmethod
    def calcular_subtotal_detalle(detalle):
        return (detalle.cantidad * detalle.precio_unitario) - detalle.descuento

    @staticmethod
    def recalcular_totales_venta(venta):
        detalles = venta.detalles.all()
        venta.subtotal = sum((detalle.subtotal for detalle in detalles), Decimal("0.00"))
        venta.impuesto = Decimal("0.00")
        venta.total = venta.subtotal - venta.descuento + venta.impuesto
        venta.save(update_fields=["subtotal", "impuesto", "total"])

    @staticmethod
    @transaction.atomic
    def descontar_inventario_por_venta(detalle):
        producto = detalle.producto

        producto.stock_actual -= detalle.cantidad
        producto.save(update_fields=["stock_actual"])

        MovimientoInventario.objects.create(
            producto=producto,
            tipo="SALIDA",
            cantidad=detalle.cantidad,
            costo_unitario=producto.costo_promedio,
            descripcion=f"Salida por venta {detalle.venta.numero_comprobante}",
        )

    @staticmethod
    @transaction.atomic
    def revertir_inventario_por_venta(detalle):
        producto = detalle.producto

        producto.stock_actual += detalle.cantidad
        producto.save(update_fields=["stock_actual"])

        MovimientoInventario.objects.create(
            producto=producto,
            tipo="AJUSTE",
            cantidad=detalle.cantidad,
            costo_unitario=producto.costo_promedio,
            descripcion=f"Reversión de venta {detalle.venta.numero_comprobante}",
        )