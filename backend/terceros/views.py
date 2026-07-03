from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Cliente, Proveedor, MedioPago
from .serializers import ClienteSerializer, ProveedorSerializer, MedioPagoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("nombre")
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all().order_by("nombre")
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]


class MedioPagoViewSet(viewsets.ModelViewSet):
    queryset = MedioPago.objects.all().order_by("nombre")
    serializer_class = MedioPagoSerializer
    permission_classes = [IsAuthenticated]