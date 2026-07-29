from decimal import Decimal

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import datetime, time, timedelta

from .models import CategoriaProducto, Producto, MovimientoInventario, UnidadMedida
from .serializers import (
    CategoriaProductoSerializer,
    ProductoSerializer,
    MovimientoInventarioSerializer,
    UnidadMedidaSerializer,
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
        "codigo",
        "nombre",
        "descripcion",
    ]

    ordering_fields = [
        "codigo",
        "nombre",
    ]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = (
        Producto.objects
        .select_related("categoria", "unidad_medida")
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
        "codigo_barras",
    ]

    @action(detail=False, methods=["get"], url_path="por-codigo-barras")
    def por_codigo_barras(self, request):
        codigo = request.query_params.get("codigo", "").strip()
        producto = self.get_queryset().filter(codigo_barras=codigo, estado=True).first()
        if not producto:
            producto = self.get_queryset().filter(codigo=codigo, estado=True).first()
        if not producto:
            return Response(
                {"detail": "No se encontró un producto con ese código."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(self.get_serializer(producto).data)

    @action(detail=False, methods=["post"], url_path="registrar-entrada")
    @transaction.atomic
    def registrar_entrada(self, request):
        codigo = str(request.data.get("codigo", "")).strip()
        try:
            cantidad = Decimal(str(request.data.get("cantidad", "0")))
            costo = Decimal(str(request.data.get("costo_unitario", "0")))
        except Exception:
            return Response(
                {"detail": "Cantidad o costo inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if cantidad <= 0 or costo < 0:
            return Response(
                {"detail": "La cantidad debe ser mayor que cero y el costo no puede ser negativo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        producto = (
            Producto.objects.select_for_update()
            .filter(codigo_barras=codigo, estado=True)
            .first()
        )
        if not producto:
            producto = (
                Producto.objects.select_for_update()
                .filter(codigo=codigo, estado=True)
                .first()
            )
        if not producto:
            return Response(
                {"detail": "No se encontró un producto con ese código."},
                status=status.HTTP_404_NOT_FOUND,
            )
        existencia_anterior = producto.stock_actual
        nuevo_total = existencia_anterior + cantidad
        if nuevo_total > 0:
            producto.costo_promedio = (
                (existencia_anterior * producto.costo_promedio) + (cantidad * costo)
            ) / nuevo_total
        producto.stock_actual = nuevo_total
        producto.save(update_fields=["stock_actual", "costo_promedio"])
        MovimientoInventario.objects.create(
            producto=producto,
            tipo="ENTRADA",
            cantidad=cantidad,
            costo_unitario=costo,
            descripcion="Entrada mediante lector de código de barras",
            usuario=request.user,
        )
        return Response(self.get_serializer(producto).data)


class UnidadMedidaViewSet(viewsets.ModelViewSet):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer
    permission_classes = [PuedeOperar]
    search_fields = ["codigo", "nombre", "simbolo"]
    ordering_fields = ["codigo", "nombre"]

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
