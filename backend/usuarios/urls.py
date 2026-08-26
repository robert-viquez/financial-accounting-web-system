from django.urls import path

from .views import (
    CambiarPasswordView,
    ConfiguracionEmpresaView,
    IdentidadEmpresaView,
    MiPerfilView,
    RolesView,
    UsuariosView,
    AuditoriaView,
)

urlpatterns = [
    path("mi-perfil/", MiPerfilView.as_view()),
    path("cambiar-password/", CambiarPasswordView.as_view()),
    path("usuarios/", UsuariosView.as_view()),
    path("roles/", RolesView.as_view()),
    path("configuracion-empresa/", ConfiguracionEmpresaView.as_view()),
    path("identidad-empresa/", IdentidadEmpresaView.as_view()),
    path("auditoria/", AuditoriaView.as_view()),
]
