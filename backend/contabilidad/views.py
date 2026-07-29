from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from .models import AsientoContable, CuentaContable, PeriodoContable
from .serializers import (
    AsientoContableSerializer,
    CuentaContableSerializer,
    PeriodoContableSerializer,
)
from .services import ContabilidadService
from .permissions import PuedeGestionarContabilidad


class CuentaContableViewSet(viewsets.ModelViewSet):
    queryset = CuentaContable.objects.select_related("cuenta_padre").all()
    serializer_class = CuentaContableSerializer
    permission_classes = [PuedeGestionarContabilidad]
    filterset_fields = ["tipo", "naturaleza", "estado", "permite_movimientos"]
    search_fields = ["codigo", "nombre"]
    ordering_fields = ["codigo", "nombre"]


class PeriodoContableViewSet(viewsets.ModelViewSet):
    queryset = PeriodoContable.objects.all()
    serializer_class = PeriodoContableSerializer
    permission_classes = [PuedeGestionarContabilidad]
    filterset_fields = ["cerrado"]


class AsientoContableViewSet(viewsets.ModelViewSet):
    queryset = (
        AsientoContable.objects.select_related("usuario")
        .prefetch_related("detalles__cuenta")
        .all()
    )
    serializer_class = AsientoContableSerializer
    permission_classes = [PuedeGestionarContabilidad]
    filterset_fields = ["estado", "origen"]
    search_fields = ["numero", "descripcion", "referencia"]
    ordering_fields = ["fecha", "numero"]
    http_method_names = ["get", "post", "head", "options"]

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def contabilizar(self, request, pk=None):
        asiento = self.get_object()
        if asiento.estado != "BORRADOR":
            return Response(
                {"detail": "Solo se puede contabilizar un borrador."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            ContabilidadService.validar_periodo_abierto(asiento.fecha)
            if asiento.total_debe <= 0 or asiento.total_debe != asiento.total_haber:
                raise DjangoValidationError("El asiento debe estar balanceado.")
            asiento.estado = "CONTABILIZADO"
            asiento.contabilizado_en = timezone.now()
            asiento.usuario = request.user
            asiento.save(update_fields=["estado", "contabilizado_en", "usuario"])
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        asiento.refresh_from_db()
        return Response(self.get_serializer(asiento).data)


def _params_fecha(request):
    return request.query_params.get("desde"), request.query_params.get("hasta")


@extend_schema(responses={200: OpenApiTypes.OBJECT})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reporte_contable(request, tipo):
    desde, hasta = _params_fecha(request)
    if tipo == "libro-diario":
        queryset = AsientoContable.objects.filter(estado="CONTABILIZADO")
        if desde:
            queryset = queryset.filter(fecha__gte=desde)
        if hasta:
            queryset = queryset.filter(fecha__lte=hasta)
        data = AsientoContableSerializer(
            queryset.prefetch_related("detalles__cuenta"),
            many=True,
        ).data
        return Response(data)

    saldos = list(ContabilidadService.reporte_saldos(desde, hasta))
    for fila in saldos:
        debe = Decimal(fila["debe"])
        haber = Decimal(fila["haber"])
        fila["saldo"] = debe - haber if fila["cuenta__naturaleza"] == "DEUDORA" else haber - debe

    if tipo == "balance-comprobacion":
        return Response(saldos)
    if tipo == "libro-mayor":
        return Response(saldos)
    if tipo == "estado-resultados":
        ingresos = sum((f["saldo"] for f in saldos if f["cuenta__tipo"] == "INGRESO"), Decimal("0"))
        costos = sum((f["saldo"] for f in saldos if f["cuenta__tipo"] in {"COSTO", "GASTO"}), Decimal("0"))
        return Response([
            {"concepto": "Ingresos", "monto": ingresos},
            {"concepto": "Costos y gastos", "monto": costos},
            {"concepto": "Utilidad neta", "monto": ingresos - costos},
        ])
    if tipo == "balance-general":
        resultado = []
        for nombre, tipos in [
            ("Activos", {"ACTIVO"}),
            ("Pasivos", {"PASIVO"}),
            ("Patrimonio", {"PATRIMONIO"}),
        ]:
            resultado.append({
                "concepto": nombre,
                "monto": sum((f["saldo"] for f in saldos if f["cuenta__tipo"] in tipos), Decimal("0")),
            })
        utilidad = sum((f["saldo"] for f in saldos if f["cuenta__tipo"] == "INGRESO"), Decimal("0")) - sum(
            (f["saldo"] for f in saldos if f["cuenta__tipo"] in {"COSTO", "GASTO"}), Decimal("0")
        )
        resultado.append({"concepto": "Resultado del periodo", "monto": utilidad})
        return Response(resultado)
    return Response({"detail": "Reporte no encontrado."}, status=status.HTTP_404_NOT_FOUND)
