from django.urls import path

from .views import (
    CambiarPasswordView,
    ConfiguracionEmpresaView,
    IdentidadEmpresaView,
    MiPerfilView,
    RolesView,
    UsuariosView,
    UsuarioDetalleView,
    PasswordAdministrativoView,
    RolDetalleView,
    PermisosView,
    InformacionSistemaView,
    AuditoriaView,
    ConfiguracionInicialAdminView,
    ConfiguracionInicialEstadoView,
)

urlpatterns = [
    path("setup/status/", ConfiguracionInicialEstadoView.as_view()),
    path("setup/admin/", ConfiguracionInicialAdminView.as_view()),
    path("mi-perfil/", MiPerfilView.as_view()),
    path("cambiar-password/", CambiarPasswordView.as_view()),
    path("usuarios/", UsuariosView.as_view()),
    path("usuarios/<int:pk>/", UsuarioDetalleView.as_view()),
    path("usuarios/<int:pk>/password/", PasswordAdministrativoView.as_view()),
    path("roles/", RolesView.as_view()),
    path("roles/<int:pk>/", RolDetalleView.as_view()),
    path("permisos/", PermisosView.as_view()),
    path("configuracion-empresa/", ConfiguracionEmpresaView.as_view()),
    path("identidad-empresa/", IdentidadEmpresaView.as_view()),
    path("auditoria/", AuditoriaView.as_view()),
    path("informacion-sistema/", InformacionSistemaView.as_view()),
]
