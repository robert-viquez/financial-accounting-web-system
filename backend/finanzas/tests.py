from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status

from config.test_utils import AccountingAPITestCase
from finanzas.models import CuentaPorCobrar, CuentaPorPagar, PagoCliente, PagoProveedor
from ventas.models import Venta
from compras.models import Compra


class FinanzasTests(AccountingAPITestCase):
    def crear_cxc(self, saldo="100.00"):
        venta = Venta.objects.create(
            cliente=self.cliente, usuario=self.user, medio_pago=self.medio_pago,
            numero_comprobante="VC-001", tipo_venta="CREDITO", total=saldo,
        )
        return CuentaPorCobrar.objects.create(
            venta=venta, cliente=self.cliente,
            fecha_vencimiento=timezone.now().date() + timedelta(days=30),
            monto_original=saldo, saldo=saldo,
        )

    def crear_cxp(self, saldo="100.00"):
        compra = Compra.objects.create(
            proveedor=self.proveedor, usuario=self.user,
            numero_factura="CC-001", tipo_compra="CREDITO", total=saldo,
        )
        return CuentaPorPagar.objects.create(
            compra=compra, proveedor=self.proveedor,
            fecha_vencimiento=timezone.now().date() + timedelta(days=30),
            monto_original=saldo, saldo=saldo,
        )

    def test_pago_parcial_y_pago_final_cliente(self):
        cuenta = self.crear_cxc()
        PagoCliente.objects.create(cuenta_por_cobrar=cuenta, medio_pago=self.medio_pago, monto="40.00")
        cuenta.refresh_from_db()
        self.assertEqual((cuenta.saldo, cuenta.estado), (Decimal("60.00"), "PARCIAL"))
        PagoCliente.objects.create(cuenta_por_cobrar=cuenta, medio_pago=self.medio_pago, monto="60.00")
        cuenta.refresh_from_db()
        self.assertEqual((cuenta.saldo, cuenta.estado), (Decimal("0.00"), "PAGADA"))

    def test_pago_superior_al_saldo_cliente_es_rechazado(self):
        cuenta = self.crear_cxc("50.00")
        with self.assertRaises(ValidationError):
            PagoCliente.objects.create(
                cuenta_por_cobrar=cuenta, medio_pago=self.medio_pago, monto="50.01"
            )
        self.assertFalse(PagoCliente.objects.exists())

    def test_api_rechaza_pago_superior_con_respuesta_400(self):
        cuenta = self.crear_cxc("50.00")
        response = self.client.post(
            "/api/pagos-clientes/",
            {
                "cuenta_por_cobrar": cuenta.pk,
                "medio_pago": self.medio_pago.pk,
                "monto": "50.01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(PagoCliente.objects.exists())

    def test_pago_parcial_y_exceso_proveedor(self):
        cuenta = self.crear_cxp()
        PagoProveedor.objects.create(cuenta_por_pagar=cuenta, medio_pago=self.medio_pago, monto="25.00")
        cuenta.refresh_from_db()
        self.assertEqual((cuenta.saldo, cuenta.estado), (Decimal("75.00"), "PARCIAL"))
        with self.assertRaises(ValidationError):
            PagoProveedor.objects.create(
                cuenta_por_pagar=cuenta, medio_pago=self.medio_pago, monto="75.01"
            )

    def test_api_de_pagos_requiere_autenticacion(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/pagos-clientes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pago_revalida_saldo_actual_y_evitar_doble_consumo(self):
        cuenta = self.crear_cxc()
        cuenta_obsoleta = CuentaPorCobrar.objects.get(pk=cuenta.pk)
        PagoCliente.objects.create(
            cuenta_por_cobrar=cuenta, medio_pago=self.medio_pago, monto="60.00"
        )
        with self.assertRaises(ValidationError):
            PagoCliente.objects.create(
                cuenta_por_cobrar=cuenta_obsoleta,
                medio_pago=self.medio_pago,
                monto="50.00",
            )
        cuenta.refresh_from_db()
        self.assertEqual(cuenta.saldo, Decimal("40.00"))
        self.assertEqual(PagoCliente.objects.count(), 1)
