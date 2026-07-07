from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CuentaPorCobrarViewSet,
    CuentaPorPagarViewSet,
    PagoClienteViewSet,
    PagoProveedorViewSet,
)

router = DefaultRouter()
router.register(r"cuentas-por-cobrar", CuentaPorCobrarViewSet)
router.register(r"pagos-clientes", PagoClienteViewSet)
router.register(r"cuentas-por-pagar", CuentaPorPagarViewSet)
router.register(r"pagos-proveedores", PagoProveedorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
