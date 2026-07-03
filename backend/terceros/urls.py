from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, ProveedorViewSet, MedioPagoViewSet

router = DefaultRouter()
router.register(r"clientes", ClienteViewSet)
router.register(r"proveedores", ProveedorViewSet)
router.register(r"medios-pago", MedioPagoViewSet)

urlpatterns = [
    path("", include(router.urls)),
]