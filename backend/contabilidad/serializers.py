from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import AsientoContable, CuentaContable, DetalleAsiento, PeriodoContable
from .services import ContabilidadService


class CuentaContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaContable
        fields = "__all__"


class PeriodoContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoContable
        fields = "__all__"

    def validate(self, attrs):
        instance = self.instance or PeriodoContable()
        for key, value in attrs.items():
            setattr(instance, key, value)
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return attrs


class DetalleAsientoSerializer(serializers.ModelSerializer):
    cuenta_codigo = serializers.CharField(source="cuenta.codigo", read_only=True)
    cuenta_nombre = serializers.CharField(source="cuenta.nombre", read_only=True)

    class Meta:
        model = DetalleAsiento
        fields = [
            "id", "cuenta", "cuenta_codigo", "cuenta_nombre",
            "descripcion", "debe", "haber",
        ]


class AsientoContableSerializer(serializers.ModelSerializer):
    detalles = DetalleAsientoSerializer(many=True)
    usuario_nombre = serializers.CharField(source="usuario.username", read_only=True)
    total_debe = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_haber = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = AsientoContable
        fields = [
            "id", "numero", "fecha", "descripcion", "origen", "referencia",
            "estado", "usuario", "usuario_nombre", "creado_en",
            "contabilizado_en", "total_debe", "total_haber", "detalles",
        ]
        read_only_fields = [
            "numero", "origen", "referencia", "estado", "usuario",
            "creado_en", "contabilizado_en",
        ]

    def create(self, validated_data):
        detalles = validated_data.pop("detalles")
        request = self.context["request"]
        try:
            return ContabilidadService.guardar_asiento(
                usuario=request.user,
                lineas=detalles,
                contabilizar=False,
                **validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
