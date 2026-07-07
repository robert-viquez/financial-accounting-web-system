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

    filterset_fields = [
        "estado",
    ]

    search_fields = [
        "nombre",
        "descripcion",
    ]

    ordering_fields = [
        "nombre",
    ]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = (
        Producto.objects
        .select_related("categoria")
        .all()
        .order_by("nombre")
    )

    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "categoria",
        "estado",
    ]

    search_fields = [
        "codigo",
        "nombre",
        "descripcion",
    ]

    ordering_fields = [
        "codigo",
        "nombre",
        "precio_venta",
        "stock_actual",
        "costo_promedio",
    ]


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        MovimientoInventario.objects
        .select_related("producto")
        .all()
        .order_by("-fecha")
    )
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "producto",
        "tipo",
    ]

    search_fields = [
        "producto__nombre",
        "descripcion",
    ]

    ordering_fields = [
        "fecha",
        "cantidad",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha_desde = self.request.query_params.get("fecha_desde")
        fecha_hasta = self.request.query_params.get("fecha_hasta")

        if fecha_desde:
            queryset = queryset.filter(fecha__date__gte=fecha_desde)

        if fecha_hasta:
            queryset = queryset.filter(fecha__date__lte=fecha_hasta)

        return queryset
