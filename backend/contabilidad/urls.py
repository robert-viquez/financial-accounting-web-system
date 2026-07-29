from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AsientoContableViewSet,
    CuentaContableViewSet,
    PeriodoContableViewSet,
    reporte_contable,
)

router = DefaultRouter()
router.register("cuentas-contables", CuentaContableViewSet)
router.register("periodos-contables", PeriodoContableViewSet)
router.register("asientos-contables", AsientoContableViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("reportes-contables/<str:tipo>/", reporte_contable),
]
