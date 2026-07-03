from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaProductoViewSet,
    ProductoViewSet,
    MovimientoInventarioViewSet,
)

router = DefaultRouter()
router.register(r"categorias-producto", CategoriaProductoViewSet)
router.register(r"productos", ProductoViewSet)
router.register(r"movimientos-inventario", MovimientoInventarioViewSet)

urlpatterns = [
    path("", include(router.urls)),
]