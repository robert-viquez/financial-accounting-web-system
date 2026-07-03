from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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