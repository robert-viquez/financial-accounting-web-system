from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Compra
from .serializers import CompraSerializer


class CompraViewSet(viewsets.ModelViewSet):
    queryset = (
        Compra.objects
        .select_related("proveedor", "usuario")
        .prefetch_related("detalles__producto")
        .all()
        .order_by("-fecha")
    )
    serializer_class = CompraSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
    "tipo_compra",
    "estado",
    "proveedor",
    ]

    search_fields = [
        "numero_factura",
        "proveedor__nombre",
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
        compra = self.get_object()
        if compra.estado == "ANULADA":
            return Response(
                {"detail": "La compra ya está anulada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for detalle in compra.detalles.select_related("producto"):
            if detalle.inventario_actualizado:
                from .services import CompraService
                CompraService.revertir_inventario_por_compra(detalle)
                detalle.inventario_actualizado = False
                detalle.save(update_fields=["inventario_actualizado"])
        compra.estado = "ANULADA"
        compra.save(update_fields=["estado"])
        if hasattr(compra, "cuenta_por_pagar"):
            compra.cuenta_por_pagar.estado = "ANULADA"
            compra.cuenta_por_pagar.save(update_fields=["estado"])
        return Response(self.get_serializer(compra).data)
