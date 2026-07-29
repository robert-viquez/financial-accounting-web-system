from django.core.management.base import BaseCommand
from django.db import transaction

from compras.models import Compra
from contabilidad.services import ContabilidadService
from finanzas.models import PagoCliente, PagoProveedor
from ventas.models import Venta


class Command(BaseCommand):
    help = "Crea o sincroniza asientos automáticos para documentos históricos."

    @transaction.atomic
    def handle(self, *args, **options):
        creados = 0
        for venta in Venta.objects.filter(estado="EMITIDA"):
            ContabilidadService.contabilizar_venta(venta)
            creados += 1
        for compra in Compra.objects.filter(estado="REGISTRADA"):
            ContabilidadService.contabilizar_compra(compra)
            creados += 1
        for pago in PagoCliente.objects.all():
            ContabilidadService.contabilizar_cobro(pago)
            creados += 1
        for pago in PagoProveedor.objects.all():
            ContabilidadService.contabilizar_pago(pago)
            creados += 1
        self.stdout.write(self.style.SUCCESS(f"Asientos sincronizados: {creados}"))
