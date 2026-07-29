from decimal import Decimal

from rest_framework import status

from compras.models import Compra
from config.test_utils import AccountingAPITestCase


class CompraTests(AccountingAPITestCase):
    def test_compra_con_varias_lineas_calcula_total_y_actualiza_stock(self):
        detalles = [
            {"producto": self.producto.pk, "cantidad": "2.00", "costo_unitario": "5.00"},
            {"producto": self.producto_2.pk, "cantidad": "3.00", "costo_unitario": "6.00"},
        ]
        response = self.client.post("/api/compras/", self.compra_payload(detalles=detalles), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        compra = Compra.objects.get()
        self.assertEqual(compra.detalles.count(), 2)
        self.assertEqual(compra.total, Decimal("28.00"))
        self.producto.refresh_from_db()
        self.producto_2.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("22.00"))
        self.assertEqual(self.producto_2.stock_actual, Decimal("18.00"))

    def test_factura_duplicada_es_rechazada(self):
        self.client.post("/api/compras/", self.compra_payload(), format="json")
        response = self.client.post("/api/compras/", self.compra_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Compra.objects.count(), 1)

    def test_linea_invalida_revierte_compra_y_movimientos_previos(self):
        detalles = [
            {"producto": self.producto.pk, "cantidad": "2.00", "costo_unitario": "5.00"},
            {"producto": self.producto_2.pk, "cantidad": "0.00", "costo_unitario": "6.00"},
        ]
        response = self.client.post("/api/compras/", self.compra_payload(detalles=detalles), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Compra.objects.exists())
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("20.00"))
    def test_anular_y_eliminar_revierten_inventario(self):
        created = self.client.post("/api/compras/", self.compra_payload(), format="json")
        response = self.client.post(f"/api/compras/{created.data['id']}/anular/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("20.00"))

        other = self.client.post("/api/compras/", self.compra_payload(numero="C-002"), format="json")
        response = self.client.delete(f"/api/compras/{other.data['id']}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("20.00"))
