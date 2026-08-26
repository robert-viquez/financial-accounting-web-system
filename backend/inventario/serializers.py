from rest_framework import serializers
from django.db import transaction
from django.utils.text import slugify

from .models import CategoriaProducto, Producto, MovimientoInventario, UnidadMedida


def siguiente_codigo_categoria(nombre):
    base = "".join(
        palabra[0] for palabra in slugify(nombre).split("-") if palabra
    ).upper()[:6] or "CAT"
    codigo = base
    consecutivo = 2
    while CategoriaProducto.objects.filter(codigo=codigo).exists():
        codigo = f"{base[:8]}{consecutivo}"
        consecutivo += 1
    return codigo

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = "__all__"
        read_only_fields = ["codigo"]

    @transaction.atomic
    def create(self, validated_data):
        validated_data["codigo"] = siguiente_codigo_categoria(validated_data["nombre"])
        return super().create(validated_data)


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True
    )
    unidad_medida_nombre = serializers.CharField(
        source="unidad_medida.nombre",
        read_only=True,
    )
    unidad_medida_simbolo = serializers.CharField(
        source="unidad_medida.simbolo",
        read_only=True,
    )

    class Meta:
        model = Producto
        fields = "__all__"
        read_only_fields = ["codigo", "stock_actual"]

    @transaction.atomic
    def create(self, validated_data):
        from usuarios.models import ConfiguracionEmpresa

        categoria = CategoriaProducto.objects.select_for_update().get(
            pk=validated_data["categoria"].pk
        )
        prefijo = (
            ConfiguracionEmpresa.objects.filter(pk=1)
            .values_list("prefijo_productos", flat=True)
            .first()
            or ""
        ).strip().upper()
        ultimo = (
            Producto.objects.filter(categoria=categoria)
            .order_by("-id")
            .first()
        )
        consecutivo = (
            Producto.objects.filter(categoria=categoria).count() + 1
            if ultimo
            else 1
        )
        base_codigo = f"{prefijo}-{categoria.codigo}" if prefijo else categoria.codigo
        codigo = f"{base_codigo}-{consecutivo:04d}"
        while Producto.objects.filter(codigo=codigo).exists():
            consecutivo += 1
            codigo = f"{base_codigo}-{consecutivo:04d}"
        validated_data["codigo"] = codigo
        if not validated_data.get("codigo_barras"):
            validated_data["codigo_barras"] = codigo
        return super().create(validated_data)

    def validate_codigo_barras(self, value):
        return value.strip() if value else None


class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = "__all__"


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source="producto.nombre",
        read_only=True
    )
    usuario_nombre = serializers.CharField(
        source="usuario.username",
        read_only=True,
        default="-",
    )
    compra_relacionada = serializers.SerializerMethodField()
    venta_relacionada = serializers.SerializerMethodField()
    unidad_medida_simbolo = serializers.CharField(
        source="producto.unidad_medida.simbolo", read_only=True, default=""
    )

    class Meta:
        model = MovimientoInventario
        fields = "__all__"

    def get_compra_relacionada(self, obj) -> str:
        descripcion = obj.descripcion or ""

        if "compra" not in descripcion.lower():
            return "-"

        return descripcion.split()[-1]

    def get_venta_relacionada(self, obj) -> str:
        descripcion = obj.descripcion or ""

        if "venta" not in descripcion.lower():
            return "-"

        return descripcion.split()[-1]
