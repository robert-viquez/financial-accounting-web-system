from django.db import connection
from django.http import JsonResponse


def health(request):
    """Report application and database readiness without exposing details."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)

    return JsonResponse({"status": "ok"})
