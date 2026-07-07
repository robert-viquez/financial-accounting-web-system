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
        read_only_fields = ["fecha_emision"]


class PagoClienteSerializer(serializers.ModelSerializer):
    medio_pago_nombre = serializers.CharField(
        source="medio_pago.nombre",
        read_only=True,
    )

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
        ]
        read_only_fields = ["fecha"]


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
        read_only_fields = ["fecha_emision"]


class PagoProveedorSerializer(serializers.ModelSerializer):
    medio_pago_nombre = serializers.CharField(
        source="medio_pago.nombre",
        read_only=True,
    )

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
        ]
        read_only_fields = ["fecha"]
