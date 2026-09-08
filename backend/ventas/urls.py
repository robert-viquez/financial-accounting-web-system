from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VentaViewSet, TipoVentaViewSet

router = DefaultRouter()
router.register(r"ventas", VentaViewSet)
router.register(r"tipos-venta", TipoVentaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
