from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from compras.models import Compra
from contabilidad.models import AsientoContable
from finanzas.models import CuentaPorCobrar, CuentaPorPagar, PagoCliente, PagoProveedor
from inventario.models import MovimientoInventario, Producto
from terceros.models import Cliente, Proveedor
from ventas.models import Venta


class SeedDemoSafetyTests(TestCase):
    @override_settings(DEBUG=False)
    @patch.dict("os.environ", {"ALLOW_DEMO_SEED": "true", "DEMO_USER_PASSWORD": "demo-test-only"})
    def test_rechaza_produccion_antes_de_borrar(self):
        User.objects.create_user("no-debe-borrarse")
        with self.assertRaisesMessage(CommandError, "DEBUG=True"):
            call_command("seed_demo", reset=True, seed=20260828)
        self.assertTrue(User.objects.filter(username="no-debe-borrarse").exists())

    @override_settings(DEBUG=True)
    @patch.dict("os.environ", {"ALLOW_DEMO_SEED": "false", "DEMO_USER_PASSWORD": "demo-test-only"})
    def test_requiere_autorizacion_explicita(self):
        with self.assertRaisesMessage(CommandError, "ALLOW_DEMO_SEED=true"):
            call_command("seed_demo", reset=True)


class SeedDemoIntegrationTests(TestCase):
    @override_settings(DEBUG=True)
    @patch.dict("os.environ", {"ALLOW_DEMO_SEED": "true", "DEMO_USER_PASSWORD": "demo-test-only"})
    def test_seed_es_reproducible_y_matematicamente_integro(self):
        output = StringIO()
        call_command("seed_demo", reset=True, seed=20260828, stdout=output)
        first = self._signature()

        self.assertIn("DEMO DATABASE VALIDATED", output.getvalue())
        self.assertEqual(first[:8], (16, 6, 17, 66, 3, 18, 12, 10))
        self.assertEqual(PagoCliente.objects.count(), 2)
        self.assertFalse(Producto.objects.filter(stock_actual__lt=0).exists())
        self.assertEqual(User.objects.get(username="cajero").groups.get().name, "Operaciones")
        self.assertFalse(User.objects.get(username="cajero").is_superuser)
        self.assertTrue(User.objects.get(username="rviquez").is_superuser)
        self.assertTrue(User.objects.get(username="rsantos").is_superuser)
        self.assertTrue(all(a.total_debe == a.total_haber for a in AsientoContable.objects.all()))
        generic_sales = Venta.objects.filter(cliente__nombre="Estimado Cliente")
        self.assertEqual(generic_sales.count(), 61)
        self.assertGreaterEqual(generic_sales.count() / Venta.objects.count(), .90)
        self.assertLessEqual(generic_sales.count() / Venta.objects.count(), .95)
        self.assertFalse(generic_sales.filter(tipo_venta="CREDITO").exists())
        self.assertEqual(
            Venta.objects.filter(tipo_venta="CREDITO").values("cliente_id").distinct().count(), 3)
        self.assertFalse(Venta.objects.filter(numero_comprobante__istartswith="DEMO-").exists())
        self.assertFalse(Compra.objects.filter(numero_factura__istartswith="DEMO-").exists())
        self.assertFalse(PagoCliente.objects.filter(referencia__istartswith="DEMO-").exists())
        self.assertFalse(PagoProveedor.objects.filter(referencia__istartswith="DEMO-").exists())
        for name in ("Natilla", "Queso Crema"):
            products = Producto.objects.filter(nombre__icontains=name)
            self.assertTrue(products.filter(stock_actual__gt=0).exists())
            self.assertTrue(MovimientoInventario.objects.filter(producto__in=products).exists())
        self.assertFalse(Proveedor.objects.filter(correo__icontains="example").exists())
        for account in CuentaPorCobrar.objects.prefetch_related("pagos"):
            self.assertEqual(account.saldo, account.monto_original - sum(p.monto for p in account.pagos.all()))
        for account in CuentaPorPagar.objects.prefetch_related("pagos"):
            self.assertEqual(account.saldo, account.monto_original - sum(p.monto for p in account.pagos.all()))

        call_command("seed_demo", reset=True, seed=20260828, stdout=StringIO())
        self.assertEqual(first, self._signature())

    @staticmethod
    def _signature():
        return (
            Cliente.objects.count(), Proveedor.objects.count(), Producto.objects.count(),
            Venta.objects.count(), Venta.objects.filter(tipo_venta="CREDITO").count(),
            Compra.objects.count(), Compra.objects.filter(tipo_compra="CREDITO").count(),
            PagoProveedor.objects.count(),
            tuple(Venta.objects.order_by("numero_comprobante").values_list("numero_comprobante", "fecha", "total")),
            tuple(Compra.objects.order_by("numero_factura").values_list("numero_factura", "fecha", "total")),
            tuple(Producto.objects.order_by("codigo").values_list("codigo", "stock_actual", "costo_promedio")),
        )
