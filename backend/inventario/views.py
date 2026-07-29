from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import datetime, time, timedelta

from .models import CategoriaProducto, Producto, MovimientoInventario
from .serializers import (
    CategoriaProductoSerializer,
    ProductoSerializer,
    MovimientoInventarioSerializer,
)
from usuarios.permissions import PuedeOperar


class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all().order_by("nombre")
    serializer_class = CategoriaProductoSerializer
    permission_classes = [PuedeOperar]

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
    permission_classes = [PuedeOperar]

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
        .select_related("producto", "usuario")
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
            desde = parse_date(fecha_desde)
            if desde:
                limite_desde = timezone.make_aware(
                    datetime.combine(desde, time.min),
                    timezone.get_current_timezone(),
                )
                queryset = queryset.filter(fecha__gte=limite_desde)

        if fecha_hasta:
            hasta = parse_date(fecha_hasta)
            if hasta:
                limite_hasta = timezone.make_aware(
                    datetime.combine(hasta + timedelta(days=1), time.min),
                    timezone.get_current_timezone(),
                )
                queryset = queryset.filter(fecha__lt=limite_hasta)

        return queryset
