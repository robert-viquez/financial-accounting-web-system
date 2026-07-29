from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CuentaPorCobrar, CuentaPorPagar, PagoCliente, PagoProveedor
from .serializers import (
    CuentaPorCobrarSerializer,
    CuentaPorPagarSerializer,
    PagoClienteSerializer,
    PagoProveedorSerializer,
)
from usuarios.permissions import PuedeOperar


class CuentaPorCobrarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CuentaPorCobrar.objects
        .select_related("venta", "cliente")
        .all()
        .order_by("fecha_vencimiento")
    )
    serializer_class = CuentaPorCobrarSerializer
    permission_classes = [PuedeOperar]

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


class PagoClienteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        PagoCliente.objects
        .select_related("cuenta_por_cobrar", "medio_pago")
        .all()
        .order_by("-fecha")
    )
    serializer_class = PagoClienteSerializer
    permission_classes = [PuedeOperar]

    filterset_fields = [
        "cuenta_por_cobrar",
        "medio_pago",
    ]
    ordering_fields = [
        "fecha",
        "monto",
    ]

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        from .services import FinanzasService
        try:
            pago = FinanzasService.anular_pago_cliente(self.get_object())
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(pago).data)


class CuentaPorPagarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CuentaPorPagar.objects
        .select_related("compra", "proveedor")
        .all()
        .order_by("fecha_vencimiento")
    )
    serializer_class = CuentaPorPagarSerializer
    permission_classes = [PuedeOperar]

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


class PagoProveedorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        PagoProveedor.objects
        .select_related("cuenta_por_pagar", "medio_pago")
        .all()
        .order_by("-fecha")
    )
    serializer_class = PagoProveedorSerializer
    permission_classes = [PuedeOperar]

    filterset_fields = [
        "cuenta_por_pagar",
        "medio_pago",
    ]
    ordering_fields = [
        "fecha",
        "monto",
    ]

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        from .services import FinanzasService
        try:
            pago = FinanzasService.anular_pago_proveedor(self.get_object())
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(pago).data)
