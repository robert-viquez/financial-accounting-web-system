from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AsientoContableViewSet,
    CuentaContableViewSet,
    PeriodoContableViewSet,
    exportar_reportes,
    reporte_contable,
    resumen_contable,
    exportar_resumen_contable,
)

router = DefaultRouter()
router.register("cuentas-contables", CuentaContableViewSet)
router.register("periodos-contables", PeriodoContableViewSet)
router.register("asientos-contables", AsientoContableViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("reportes-contables/<str:tipo>/", reporte_contable),
    path("resumen-contable/", resumen_contable),
    path("resumen-contable/exportar/xlsx/", exportar_resumen_contable),
    path("reportes/exportar/<str:formato>/", exportar_reportes),
]
