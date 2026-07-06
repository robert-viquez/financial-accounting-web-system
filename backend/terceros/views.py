from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Cliente, Proveedor, MedioPago
from .serializers import ClienteSerializer, ProveedorSerializer, MedioPagoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("nombre")
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
    "estado",
    ]

    search_fields = [
        "nombre",
        "identificacion",
        "correo",
    ]

    ordering_fields = [
        "nombre",
        "identificacion",
    ]

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all().order_by("nombre")
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]
 
    filterset_fields = [
    "estado",
    ]

    search_fields = [
        "nombre",
        "identificacion",
        "correo",
    ]

    ordering_fields = [
        "nombre",
    ]

class MedioPagoViewSet(viewsets.ModelViewSet):
    queryset = MedioPago.objects.all().order_by("nombre")
    serializer_class = MedioPagoSerializer
    permission_classes = [IsAuthenticated]