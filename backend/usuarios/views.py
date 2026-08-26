from django.contrib.auth.models import Group, User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import ConfiguracionEmpresa, RegistroAuditoria
from .serializers import (
    CambiarPasswordSerializer,
    ConfiguracionEmpresaSerializer,
    IdentidadEmpresaSerializer,
    UsuarioSerializer,
    RegistroAuditoriaSerializer,
    RolSerializer,
)


class MiPerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
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


class UsuariosView(generics.ListAPIView):
    queryset = User.objects.prefetch_related("groups").order_by("username")
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAdminUser]


class RolesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: RolSerializer(many=True)})
    def get(self, request):
        return Response([
            {"nombre": group.name, "descripcion": f"Permisos del rol {group.name}."}
            for group in Group.objects.order_by("name")
        ])


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
    filterset_fields = ["usuario", "metodo", "codigo_respuesta"]
    search_fields = ["ruta", "usuario__username"]
