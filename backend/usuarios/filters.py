import django_filters

from .models import RegistroAuditoria


class RegistroAuditoriaFilter(django_filters.FilterSet):
    desde = django_filters.IsoDateTimeFilter(field_name="fecha", lookup_expr="gte")
    hasta = django_filters.IsoDateTimeFilter(field_name="fecha", lookup_expr="lte")

    class Meta:
        model = RegistroAuditoria
        fields = ["usuario", "metodo", "codigo_respuesta", "desde", "hasta"]
