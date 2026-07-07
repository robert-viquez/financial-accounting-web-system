from rest_framework import serializers
from .models import CategoriaProducto, Producto, MovimientoInventario

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = "__all__"


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True
    )

    class Meta:
        model = Producto
        fields = "__all__"


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source="producto.nombre",
        read_only=True
    )
    usuario_nombre = serializers.SerializerMethodField()
    compra_relacionada = serializers.SerializerMethodField()
    venta_relacionada = serializers.SerializerMethodField()

    class Meta:
        model = MovimientoInventario
        fields = "__all__"

    def get_usuario_nombre(self, obj):
        return "-"

    def get_compra_relacionada(self, obj):
        descripcion = obj.descripcion or ""

        if "compra" not in descripcion.lower():
            return "-"

        return descripcion.split()[-1]

    def get_venta_relacionada(self, obj):
        descripcion = obj.descripcion or ""

        if "venta" not in descripcion.lower():
            return "-"

        return descripcion.split()[-1]
