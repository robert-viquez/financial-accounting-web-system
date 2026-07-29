from rest_framework.permissions import BasePermission, SAFE_METHODS


class PuedeGestionarContabilidad(BasePermission):
    message = "Se requiere el rol Contabilidad o Administrador."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.groups.filter(
                    name__in=["Contabilidad", "Administrador"]
                ).exists()
            )
        )
