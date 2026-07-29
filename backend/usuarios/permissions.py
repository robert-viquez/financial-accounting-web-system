from rest_framework.permissions import BasePermission, SAFE_METHODS


class PuedeOperar(BasePermission):
    message = "Se requiere el rol Operaciones o Administrador."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user.is_staff
            or request.user.groups.filter(
                name__in=["Operaciones", "Administrador"]
            ).exists()
        )
