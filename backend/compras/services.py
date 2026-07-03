from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from inventario.models import MovimientoInventario


class CompraService:
    @staticmethod
    def validar_detalle_compra(detalle):
        if detalle.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")

        if detalle.costo_unitario < 0:
            raise ValidationError("El costo unitario no puede ser negativo.")

        subtotal = detalle.cantidad * detalle.costo_unitario

        if subtotal < 0:
            raise ValidationError("El subtotal no puede ser negativo.")

    @staticmethod
    def calcular_subtotal_detalle(detalle):
        return detalle.cantidad * detalle.costo_unitario

    @staticmethod
    def recalcular_totales_compra(compra):
        detalles = compra.detalles.all()
        compra.subtotal = sum((detalle.subtotal for detalle in detalles), Decimal("0.00"))
        compra.impuesto = Decimal("0.00")
        compra.total = compra.subtotal + compra.impuesto
        compra.save(update_fields=["subtotal", "impuesto", "total"])

    @staticmethod
    @transaction.atomic
    def actualizar_inventario_por_compra(detalle):
        producto = detalle.producto

        stock_anterior = producto.stock_actual
        costo_anterior = producto.costo_promedio

        cantidad_nueva = detalle.cantidad
        costo_nuevo = detalle.costo_unitario

        valor_anterior = stock_anterior * costo_anterior
        valor_nuevo = cantidad_nueva * costo_nuevo

        stock_total = stock_anterior + cantidad_nueva

        if stock_total > 0:
            producto.costo_promedio = (valor_anterior + valor_nuevo) / stock_total

        producto.stock_actual = stock_total
        producto.save(update_fields=["stock_actual", "costo_promedio"])

        MovimientoInventario.objects.create(
            producto=producto,
            tipo="ENTRADA",
            cantidad=detalle.cantidad,
            costo_unitario=detalle.costo_unitario,
            descripcion=f"Entrada por compra {detalle.compra.numero_factura}",
        )

    @staticmethod
    @transaction.atomic
    def revertir_inventario_por_compra(detalle):
        producto = detalle.producto

        if producto.stock_actual < detalle.cantidad:
            raise ValidationError(
                "No se puede revertir la compra porque el stock actual es menor que la cantidad comprada."
            )

        producto.stock_actual -= detalle.cantidad
        producto.save(update_fields=["stock_actual"])

        MovimientoInventario.objects.create(
            producto=producto,
            tipo="AJUSTE",
            cantidad=detalle.cantidad,
            costo_unitario=detalle.costo_unitario,
            descripcion=f"Reversión de compra {detalle.compra.numero_factura}",
        )