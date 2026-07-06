from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
    