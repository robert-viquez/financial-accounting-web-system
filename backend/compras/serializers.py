from rest_framework import serializers
from django.db import transaction

from .models import Compra, DetalleCompra


class DetalleCompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source="producto.nombre",
        read_only=True
    )

    class Meta:
        model = DetalleCompra
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "cantidad",
            "costo_unitario",
            "subtotal",
            "inventario_actualizado",
        ]
        read_only_fields = ["subtotal", "inventario_actualizado"]

    def validate(self, attrs):
        detalle = DetalleCompra(**attrs)
        try:
            from .services import CompraService
            CompraService.validar_detalle_compra(detalle)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(exc.messages) from exc
            raise
        return attrs


class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)
    proveedor_nombre = serializers.CharField(
        source="proveedor.nombre",
        read_only=True
    )
    usuario_nombre = serializers.CharField(
        source="usuario.username",
        read_only=True
    )

    class Meta:
        model = Compra
        fields = [
            "id",
            "proveedor",
            "proveedor_nombre",
            "usuario",
            "usuario_nombre",
            "numero_factura",
            "fecha",
            "tipo_compra",
            "subtotal",
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
        detalles_data = validated_data.pop("detalles")
        usuario = self.context["request"].user

        compra = Compra.objects.create(
            usuario=usuario,
            **validated_data
        )

        for detalle_data in detalles_data:
            DetalleCompra.objects.create(
                compra=compra,
                **detalle_data
            )

        compra.refresh_from_db()
        return compra
