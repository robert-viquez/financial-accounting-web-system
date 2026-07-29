from rest_framework import serializers
from django.db import transaction
from .models import Venta, DetalleVenta

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source="producto.nombre",
        read_only=True
    )

    class Meta:
        model = DetalleVenta
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "cantidad",
            "precio_unitario",
            "descuento",
            "subtotal",
            "inventario_descontado",
        ]
        read_only_fields = ["subtotal", "inventario_descontado"]

    def validate(self, attrs):
        detalle = DetalleVenta(**attrs)
        try:
            from .services import VentaService
            VentaService.validar_detalle_venta(detalle)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(exc.messages) from exc
            raise
        return attrs


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)
    cliente_nombre = serializers.CharField(
        source="cliente.nombre",
        read_only=True
    )
    medio_pago_nombre = serializers.CharField(
        source="medio_pago.nombre",
        read_only=True
    )
    usuario_nombre = serializers.CharField(
        source="usuario.username",
        read_only=True
    )

    class Meta:
        model = Venta
        fields = [
            "id",
            "cliente",
            "cliente_nombre",
            "usuario",
            "usuario_nombre",
            "medio_pago",
            "medio_pago_nombre",
            "numero_comprobante",
            "fecha",
            "tipo_venta",
            "subtotal",
            "descuento",
            "impuesto",
            "total",
            "estado",
            "observaciones",
            "detalles",
        ]
        read_only_fields = [
            "usuario",
            "fecha",
            "subtotal",
            "impuesto",
            "total",
            "estado",
        ]

    @transaction.atomic
    def create(self, validated_data):
        from django.core.exceptions import ValidationError as DjangoValidationError

        detalles_data = validated_data.pop("detalles")
        usuario = self.context["request"].user
        try:
            venta = Venta.objects.create(
                usuario=usuario,
                **validated_data
            )

            for detalle_data in detalles_data:
                DetalleVenta.objects.create(
                    venta=venta,
                    **detalle_data
                )

            venta.refresh_from_db()
            return venta
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
