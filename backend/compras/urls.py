from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompraViewSet

router = DefaultRouter()
router.register(r"compras", CompraViewSet)

urlpatterns = [
    path("", include(router.urls)),
]