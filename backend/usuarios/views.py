from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.db import connection
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import ConfiguracionEmpresa, RegistroAuditoria
from .filters import RegistroAuditoriaFilter
from .serializers import (
    CambiarPasswordSerializer,
    ConfiguracionEmpresaSerializer,
    IdentidadEmpresaSerializer,
    PerfilSerializer,
    UsuarioAdminSerializer,
    PasswordAdministrativoSerializer,
    PermisoSerializer,
    RolAdminSerializer,
    RegistroAuditoriaSerializer,
)


class MiPerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CambiarPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=CambiarPasswordSerializer, responses={200: dict})
    def post(self, request):
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["nueva"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Contraseña actualizada correctamente."})


class UsuariosView(generics.ListCreateAPIView):
    queryset = User.objects.prefetch_related("groups").order_by("username")
    serializer_class = UsuarioAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["username", "first_name", "last_name", "email"]
    filterset_fields = ["is_active", "is_staff", "is_superuser", "groups"]
    ordering_fields = ["username", "first_name", "last_name", "email", "is_active"]


class UsuarioDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.prefetch_related("groups")
    serializer_class = UsuarioAdminSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_destroy(self, instance):
        if instance == self.request.user:
            self.permission_denied(self.request, message="No puede eliminar su propia cuenta.")
        if instance.is_superuser:
            self.permission_denied(self.request, message="Los superusuarios no se eliminan desde FAWS.")
        if instance.registroauditoria_set.exists():
            self.permission_denied(
                self.request, message="El usuario tiene historial. Desactívelo en lugar de eliminarlo."
            )
        try:
            instance.delete()
        except ProtectedError:
            self.permission_denied(
                self.request, message="El usuario tiene registros relacionados. Desactívelo."
            )


class PasswordAdministrativoView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        target = generics.get_object_or_404(User, pk=pk)
        if target.is_superuser and not request.user.is_superuser:
            self.permission_denied(request, message="Solo un superusuario puede modificar otro superusuario.")
        serializer = PasswordAdministrativoSerializer(
            data=request.data, context={"target_user": target}
        )
        serializer.is_valid(raise_exception=True)
        target.set_password(serializer.validated_data["password"])
        target.save(update_fields=["password"])
        return Response({"detail": "Contraseña actualizada correctamente."})


class RolesView(generics.ListCreateAPIView):
    queryset = Group.objects.prefetch_related("permissions", "user_set").order_by("name")
    serializer_class = RolAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None


class RolDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.prefetch_related("permissions", "user_set")
    serializer_class = RolAdminSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_destroy(self, instance):
        if instance.user_set.exists():
            self.permission_denied(request=self.request, message="No se puede eliminar un rol asignado a usuarios.")
        instance.delete()


class PermisosView(generics.ListAPIView):
    queryset = Permission.objects.select_related("content_type").exclude(
        content_type__app_label__in=["admin", "auth", "contenttypes", "sessions"]
    ).order_by("content_type__app_label", "content_type__model", "codename")
    serializer_class = PermisoSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    search_fields = ["name", "codename", "content_type__app_label", "content_type__model"]


class ConfiguracionEmpresaView(generics.RetrieveUpdateAPIView):
    serializer_class = ConfiguracionEmpresaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        configuracion, _ = ConfiguracionEmpresa.objects.get_or_create(pk=1)
        return configuracion

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message="Solo un administrador puede modificar la configuración.",
            )
        serializer.save()


class IdentidadEmpresaView(generics.RetrieveAPIView):
    serializer_class = IdentidadEmpresaSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        configuracion, _ = ConfiguracionEmpresa.objects.get_or_create(pk=1)
        return configuracion



class AuditoriaView(generics.ListAPIView):
    queryset = RegistroAuditoria.objects.select_related("usuario").all()
    serializer_class = RegistroAuditoriaSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_class = RegistroAuditoriaFilter
    search_fields = ["ruta", "usuario__username"]
    ordering_fields = ["fecha", "usuario", "metodo", "codigo_respuesta", "ruta"]


class InformacionSistemaView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response({
            "version_aplicacion": settings.SPECTACULAR_SETTINGS.get("VERSION"),
            "entorno": "Desarrollo" if settings.DEBUG else "Producción",
            "framework": f"Django {__import__('django').get_version()}",
            "base_datos": connection.vendor,
            "estado": "ok",
            "debug": settings.DEBUG,
            "https": request.is_secure(),
            "hora_servidor": timezone.now(),
        })
