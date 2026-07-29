from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Venta
from .serializers import VentaSerializer


class VentaViewSet(viewsets.ModelViewSet):
    queryset = (
        Venta.objects
        .select_related("cliente", "usuario", "medio_pago")
        .prefetch_related("detalles__producto")
        .all()
        .order_by("-fecha")
    )
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]
  
    filterset_fields = [
    "tipo_venta",
    "estado",
    "cliente",
    ]

    search_fields = [
        "numero_comprobante",
        "cliente__nombre",
    ]

    ordering_fields = [
        "fecha",
        "total",
    ]

    @transaction.atomic
    def perform_destroy(self, instance):
        for detalle in list(instance.detalles.select_related("producto")):
            detalle.delete()
        instance.delete()

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def anular(self, request, pk=None):
        venta = self.get_object()
        if venta.estado == "ANULADA":
            return Response(
                {"detail": "La venta ya está anulada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for detalle in venta.detalles.select_related("producto"):
            if detalle.inventario_descontado:
                from .services import VentaService
                VentaService.revertir_inventario_por_venta(detalle)
                detalle.inventario_descontado = False
                detalle.save(update_fields=["inventario_descontado"])
        venta.estado = "ANULADA"
        venta.save(update_fields=["estado"])
        if hasattr(venta, "cuenta_por_cobrar"):
            venta.cuenta_por_cobrar.estado = "ANULADA"
            venta.cuenta_por_cobrar.save(update_fields=["estado"])
        return Response(self.get_serializer(venta).data)
