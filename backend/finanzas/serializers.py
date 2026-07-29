from rest_framework import serializers

from .models import CuentaPorCobrar, CuentaPorPagar, PagoCliente, PagoProveedor


class CuentaPorCobrarSerializer(serializers.ModelSerializer):
    venta_numero = serializers.CharField(
        source="venta.numero_comprobante",
        read_only=True,
    )
    cliente_nombre = serializers.CharField(
        source="cliente.nombre",
        read_only=True,
    )

    class Meta:
        model = CuentaPorCobrar
        fields = [
            "id",
            "venta",
            "venta_numero",
            "cliente",
            "cliente_nombre",
            "fecha_emision",
            "fecha_vencimiento",
            "monto_original",
            "saldo",
            "estado",
        ]
        read_only_fields = [
            "venta",
            "cliente",
            "fecha_emision",
            "fecha_vencimiento",
            "monto_original",
            "saldo",
            "estado",
        ]


class PagoClienteSerializer(serializers.ModelSerializer):
    medio_pago_nombre = serializers.CharField(
        source="medio_pago.nombre",
        read_only=True,
    )
    usuario_nombre = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = PagoCliente
        fields = [
            "id",
            "cuenta_por_cobrar",
            "medio_pago",
            "medio_pago_nombre",
            "fecha",
            "monto",
            "referencia",
            "observaciones",
            "usuario",
            "usuario_nombre",
            "estado",
            "anulado_en",
        ]
        read_only_fields = ["fecha", "usuario", "estado", "anulado_en"]

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        try:
            return super().create(validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(exc.messages) from exc
            raise


class CuentaPorPagarSerializer(serializers.ModelSerializer):
    compra_numero = serializers.CharField(
        source="compra.numero_factura",
        read_only=True,
    )
    proveedor_nombre = serializers.CharField(
        source="proveedor.nombre",
        read_only=True,
    )

    class Meta:
        model = CuentaPorPagar
        fields = [
            "id",
            "compra",
            "compra_numero",
            "proveedor",
            "proveedor_nombre",
            "fecha_emision",
            "fecha_vencimiento",
            "monto_original",
            "saldo",
            "estado",
        ]
        read_only_fields = [
            "compra",
            "proveedor",
            "fecha_emision",
            "fecha_vencimiento",
            "monto_original",
            "saldo",
            "estado",
        ]


class PagoProveedorSerializer(serializers.ModelSerializer):
    medio_pago_nombre = serializers.CharField(
        source="medio_pago.nombre",
        read_only=True,
    )
    usuario_nombre = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = PagoProveedor
        fields = [
            "id",
            "cuenta_por_pagar",
            "medio_pago",
            "medio_pago_nombre",
            "fecha",
            "monto",
            "referencia",
            "observaciones",
            "usuario",
            "usuario_nombre",
            "estado",
            "anulado_en",
        ]
        read_only_fields = ["fecha", "usuario", "estado", "anulado_en"]

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        try:
            return super().create(validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(exc.messages) from exc
            raise
