from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from django.http import HttpResponse
from django.utils.dateparse import parse_date
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
from .reporting import REPORT_TITLES, build_accounting_summary_xlsx, build_pdf, build_xlsx
from config.pagination import StandardResultsSetPagination


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


def _resumen_params(request):
    periodo_id = request.query_params.get("periodo")
    desde, hasta = _params_fecha(request)
    period_label = f"Período: {desde or 'inicio'} al {hasta or 'hoy'}"
    if periodo_id:
        periodo = PeriodoContable.objects.get(pk=periodo_id)
        desde, hasta = periodo.fecha_inicio, periodo.fecha_fin
        period_label = periodo.nombre
    return desde, hasta, period_label


def _resumen_rows(request):
    desde, hasta, period_label = _resumen_params(request)
    rows = list(ContabilidadService.reporte_saldos(desde, hasta))
    search = request.query_params.get("search", "").strip()
    account_type = request.query_params.get("tipo", "").strip()
    nature = request.query_params.get("naturaleza", "").strip()
    result = []
    for row in rows:
        if account_type and row["cuenta__tipo"] != account_type:
            continue
        if nature and row["cuenta__naturaleza"] != nature:
            continue
        haystack = " ".join(str(row[key]) for key in (
            "cuenta__codigo", "cuenta__nombre", "cuenta__tipo", "cuenta__naturaleza"
        )).lower()
        if search and search.lower() not in haystack:
            continue
        debit, credit = Decimal(row["debe"]), Decimal(row["haber"])
        balance = debit - credit if row["cuenta__naturaleza"] == "DEUDORA" else credit - debit
        result.append({
            "codigo": row["cuenta__codigo"], "cuenta": row["cuenta__nombre"],
            "tipo": row["cuenta__tipo"], "naturaleza": row["cuenta__naturaleza"],
            "debitos": debit, "creditos": credit, "saldo": balance,
        })
    ordering = request.query_params.get("ordering", "codigo")
    reverse = ordering.startswith("-")
    key = ordering.lstrip("-")
    if key not in {"codigo", "cuenta", "tipo", "naturaleza", "debitos", "creditos", "saldo"}:
        key = "codigo"
    result.sort(key=lambda item: item[key], reverse=reverse)
    totals = {
        "debitos": sum((item["debitos"] for item in result), Decimal("0")),
        "creditos": sum((item["creditos"] for item in result), Decimal("0")),
        "saldo": sum((item["saldo"] for item in result), Decimal("0")),
    }
    return result, totals, desde, hasta, period_label


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumen_contable(request):
    try:
        rows, totals, _, _, _ = _resumen_rows(request)
    except PeriodoContable.DoesNotExist:
        return Response({"detail": "El período seleccionado no existe."}, status=status.HTTP_400_BAD_REQUEST)
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(rows, request)
    response = paginator.get_paginated_response(page)
    response.data["totals"] = totals
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exportar_resumen_contable(request):
    try:
        rows, totals, desde, hasta, period_label = _resumen_rows(request)
    except PeriodoContable.DoesNotExist:
        return Response({"detail": "El período seleccionado no existe."}, status=status.HTTP_400_BAD_REQUEST)
    content = build_accounting_summary_xlsx(rows, totals, period_label)
    suffix = f"{desde}_{hasta}" if desde or hasta else str(timezone.localdate())
    response = HttpResponse(content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="resumen_contable_{suffix}.xlsx"'
    response["X-Content-Type-Options"] = "nosniff"
    return response


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


@extend_schema(request=OpenApiTypes.OBJECT, responses={(200, "application/octet-stream"): bytes})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def exportar_reportes(request, formato):
    reportes = request.data.get("reportes") or []
    if not isinstance(reportes, list) or not reportes:
        return Response({"detail": "Seleccione al menos un reporte."}, status=status.HTTP_400_BAD_REQUEST)
    invalidos = [reporte for reporte in reportes if reporte not in REPORT_TITLES]
    if invalidos:
        return Response({"detail": "La selección contiene reportes no válidos."}, status=status.HTTP_400_BAD_REQUEST)
    desde_raw, hasta_raw = request.data.get("desde"), request.data.get("hasta")
    desde = parse_date(desde_raw) if desde_raw else None
    hasta = parse_date(hasta_raw) if hasta_raw else None
    if (desde_raw and not desde) or (hasta_raw and not hasta):
        return Response({"detail": "Las fechas indicadas no son válidas."}, status=status.HTTP_400_BAD_REQUEST)
    if desde and hasta and desde > hasta:
        return Response({"detail": "La fecha inicial no puede ser posterior a la fecha final."}, status=status.HTTP_400_BAD_REQUEST)
    if formato == "xlsx":
        content = build_xlsx(reportes, desde, hasta)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"
    elif formato == "pdf":
        content = build_pdf(reportes, desde, hasta)
        content_type = "application/pdf"
        extension = "pdf"
    else:
        return Response({"detail": "Formato de exportación no soportado."}, status=status.HTTP_404_NOT_FOUND)
    period = f"{desde or 'inicio'}_{hasta or timezone.localdate()}"
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="QuesoLosSantos_Reportes_{period}.{extension}"'
    response["X-Content-Type-Options"] = "nosniff"
    return response
