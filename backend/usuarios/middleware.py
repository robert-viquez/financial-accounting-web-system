from .models import RegistroAuditoria


class AuditoriaMiddleware:
    METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method in self.METHODS
            and request.path.startswith("/api/")
            and request.user.is_authenticated
        ):
            RegistroAuditoria.objects.create(
                usuario=request.user,
                metodo=request.method,
                ruta=request.path[:255],
                codigo_respuesta=response.status_code,
                direccion_ip=self._ip(request),
            )
        return response

    @staticmethod
    def _ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        return (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")) or None
