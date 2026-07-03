from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import CategoriaProducto, Producto, MovimientoInventario
from .serializers import (
    CategoriaProductoSerializer,
    ProductoSerializer,
    MovimientoInventarioSerializer,
)


class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all().order_by("nombre")
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related("categoria").all().order_by("nombre")
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoInventario.objects.select_related("producto").all().order_by("-fecha")
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated]