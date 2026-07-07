from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import CuentaPorCobrar, CuentaPorPagar, PagoCliente, PagoProveedor
from .serializers import (
    CuentaPorCobrarSerializer,
    CuentaPorPagarSerializer,
    PagoClienteSerializer,
    PagoProveedorSerializer,
)


class CuentaPorCobrarViewSet(viewsets.ModelViewSet):
    queryset = (
        CuentaPorCobrar.objects
        .select_related("venta", "cliente")
        .all()
        .order_by("fecha_vencimiento")
    )
    serializer_class = CuentaPorCobrarSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "estado",
        "cliente",
    ]
    search_fields = [
        "venta__numero_comprobante",
        "cliente__nombre",
    ]
    ordering_fields = [
        "fecha_vencimiento",
        "saldo",
        "monto_original",
    ]


class PagoClienteViewSet(viewsets.ModelViewSet):
    queryset = (
        PagoCliente.objects
        .select_related("cuenta_por_cobrar", "medio_pago")
        .all()
        .order_by("-fecha")
    )
    serializer_class = PagoClienteSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "cuenta_por_cobrar",
        "medio_pago",
    ]
    ordering_fields = [
        "fecha",
        "monto",
    ]


class CuentaPorPagarViewSet(viewsets.ModelViewSet):
    queryset = (
        CuentaPorPagar.objects
        .select_related("compra", "proveedor")
        .all()
        .order_by("fecha_vencimiento")
    )
    serializer_class = CuentaPorPagarSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "estado",
        "proveedor",
    ]
    search_fields = [
        "compra__numero_factura",
        "proveedor__nombre",
    ]
    ordering_fields = [
        "fecha_vencimiento",
        "saldo",
        "monto_original",
    ]


class PagoProveedorViewSet(viewsets.ModelViewSet):
    queryset = (
        PagoProveedor.objects
        .select_related("cuenta_por_pagar", "medio_pago")
        .all()
        .order_by("-fecha")
    )
    serializer_class = PagoProveedorSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "cuenta_por_pagar",
        "medio_pago",
    ]
    ordering_fields = [
        "fecha",
        "monto",
    ]
