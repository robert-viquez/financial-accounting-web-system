from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from compras.models import Compra
from contabilidad.models import AsientoContable
from finanzas.models import CuentaPorCobrar, CuentaPorPagar, PagoCliente, PagoProveedor
from inventario.models import MovimientoInventario, Producto
from terceros.models import Cliente, Proveedor
from usuarios.models import ConfiguracionEmpresa
from ventas.models import Venta


class SeedDemoSafetyTests(TestCase):
    @patch.dict("os.environ", {"ALLOW_DEMO_SEED": "false", "DEMO_PASSWORD": "demo-test-only"})
    def test_requiere_autorizacion_antes_de_borrar(self):
        User.objects.create_user("no-debe-borrarse")
        with self.assertRaisesMessage(CommandError, "ALLOW_DEMO_SEED=true"):
            call_command("seed_demo", reset=True, seed=20260828)
        self.assertTrue(User.objects.filter(username="no-debe-borrarse").exists())

    @override_settings(DEBUG=True)
    @patch.dict("os.environ", {"ALLOW_DEMO_SEED": "false", "DEMO_PASSWORD": "demo-test-only"})
    def test_requiere_autorizacion_explicita(self):
        with self.assertRaisesMessage(CommandError, "ALLOW_DEMO_SEED=true"):
            call_command("seed_demo", reset=True)


class SeedDemoIntegrationTests(TestCase):
    @override_settings(DEBUG=False)
    @patch.dict("os.environ", {"ALLOW_DEMO_SEED": "true", "DEMO_USERNAME": "demo", "DEMO_PASSWORD": "demo-test-only"})
    def test_seed_es_reproducible_y_matematicamente_integro(self):
        technical = User.objects.create_superuser(
            "technical-admin",
            email="technical@example.test",
            password="technical-password-unchanged",
        )
        technical_password_hash = technical.password
        output = StringIO()
        call_command("seed_demo", reset=True, seed=20260828, stdout=output)
        first = self._signature()

        self.assertIn("DEMO DATABASE VALIDATED", output.getvalue())
        technical.refresh_from_db()
        self.assertEqual(technical.username, "technical-admin")
        self.assertEqual(technical.email, "technical@example.test")
        self.assertEqual(technical.password, technical_password_hash)
        self.assertTrue(technical.check_password("technical-password-unchanged"))
        self.assertTrue(technical.is_staff)
        self.assertTrue(technical.is_superuser)
        self.assertEqual(first[:8], (16, 6, 20, 66, 3, 18, 12, 10))
        self.assertEqual(PagoCliente.objects.count(), 2)
        self.assertFalse(Producto.objects.filter(stock_actual__lt=0).exists())
        demo = User.objects.get(username="demo")
        self.assertEqual(demo.groups.get().name, "Operaciones")
        self.assertFalse(demo.is_staff)
        self.assertFalse(demo.is_superuser)
        self.assertTrue(Group.objects.filter(name="Ventas").exists())
        self.assertTrue(Group.objects.filter(name="Inventario").exists())
        self.assertTrue(Group.objects.filter(name="Gerencia").exists())
        self.assertTrue(demo.check_password("demo-test-only"))
        self.assertEqual(ConfiguracionEmpresa.objects.get(pk=1).nombre, "ByteForge Technologies")
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
        for code in ("CPU-001", "GPU-001", "SSD-001", "LAP-001", "NET-001"):
            products = Producto.objects.filter(codigo=code)
            self.assertTrue(products.filter(stock_actual__gt=0).exists())
            self.assertTrue(MovimientoInventario.objects.filter(producto__in=products).exists())
        self.assertFalse(Proveedor.objects.filter(correo__icontains="example").exists())
        for account in CuentaPorCobrar.objects.prefetch_related("pagos"):
            self.assertEqual(account.saldo, account.monto_original - sum(p.monto for p in account.pagos.all()))
        for account in CuentaPorPagar.objects.prefetch_related("pagos"):
            self.assertEqual(account.saldo, account.monto_original - sum(p.monto for p in account.pagos.all()))

        demo.set_password("changed-between-resets")
        demo.save(update_fields=["password"])
        call_command("seed_demo", reset=True, seed=20260828, stdout=StringIO())
        self.assertEqual(first, self._signature())
        self.assertTrue(User.objects.get(username="demo").check_password("demo-test-only"))
        technical.refresh_from_db()
        self.assertEqual(technical.password, technical_password_hash)
        self.assertTrue(technical.is_staff)
        self.assertTrue(technical.is_superuser)

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
