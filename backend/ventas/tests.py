from decimal import Decimal

from django.db import IntegrityError
from rest_framework import status

from config.test_utils import AccountingAPITestCase
from inventario.models import MovimientoInventario
from ventas.models import Venta


class VentaTests(AccountingAPITestCase):
    def test_rechaza_inventario_insuficiente_y_revierte_toda_la_venta(self):
        response = self.client.post(
            "/api/ventas/",
            self.venta_payload(detalles=[{
                "producto": self.producto.pk,
                "cantidad": "21.00",
                "precio_unitario": "10.00",
                "descuento": "0.00",
            }]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Venta.objects.exists())
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("20.00"))

    def test_venta_con_varias_lineas_calcula_total_y_descuenta_stock(self):
        detalles = [
            {"producto": self.producto.pk, "cantidad": "2.00", "precio_unitario": "10.00", "descuento": "1.00"},
            {"producto": self.producto_2.pk, "cantidad": "3.00", "precio_unitario": "5.00", "descuento": "0.00"},
        ]
        response = self.client.post("/api/ventas/", self.venta_payload(detalles=detalles), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        venta = Venta.objects.get()
        self.assertEqual(venta.detalles.count(), 2)
        self.assertEqual(venta.total, Decimal("34.00"))
        self.producto.refresh_from_db()
        self.producto_2.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("18.00"))
        self.assertEqual(self.producto_2.stock_actual, Decimal("12.00"))
    def test_numero_comprobante_duplicado_es_rechazado(self):
        first = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        second = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Venta.objects.count(), 1)

    def test_anular_reintegra_inventario_una_sola_vez(self):
        created = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        url = f"/api/ventas/{created.data['id']}/anular/"
        response = self.client.post(url)
        repeated = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(repeated.status_code, status.HTTP_400_BAD_REQUEST)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("20.00"))
        self.assertEqual(MovimientoInventario.objects.count(), 2)

    def test_eliminar_venta_reintegra_inventario(self):
        created = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        response = self.client.delete(f"/api/ventas/{created.data['id']}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("20.00"))
