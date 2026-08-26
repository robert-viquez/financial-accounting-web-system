from decimal import Decimal

from django.db import IntegrityError
from rest_framework import status

from config.test_utils import AccountingAPITestCase
from inventario.models import MovimientoInventario, UnidadMedida
from ventas.models import DetalleVenta, Venta


class VentaTests(AccountingAPITestCase):
    def test_venta_por_peso_usa_la_misma_cantidad_en_detalle_movimiento_y_stock(self):
        kg, _ = UnidadMedida.objects.get_or_create(
            codigo="KG", defaults={"nombre": "Kilogramo", "simbolo": "kg", "permite_decimales": True}
        )
        self.producto.unidad_medida = kg
        self.producto.save(update_fields=["unidad_medida"])
        response = self.client.post(
            "/api/ventas/",
            self.venta_payload(detalles=[{
                "producto": self.producto.pk, "cantidad": "0.385",
                "precio_unitario": "5200.00", "descuento": "0.00",
            }]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        detail = Venta.objects.get().detalles.get()
        move = MovimientoInventario.objects.get(tipo="SALIDA")
        self.producto.refresh_from_db()
        self.assertEqual(detail.cantidad, Decimal("0.385"))
        self.assertEqual(move.cantidad, detail.cantidad)
        self.assertEqual(self.producto.stock_actual, Decimal("19.615"))

    def test_venta_desde_monto_normaliza_una_vez_para_detalle_subtotal_y_movimiento(self):
        kg, _ = UnidadMedida.objects.get_or_create(
            codigo="KG", defaults={"nombre": "Kilogramo", "simbolo": "kg", "permite_decimales": True}
        )
        self.producto.unidad_medida = kg
        self.producto.precio_venta = Decimal("5200.00")
        self.producto.save(update_fields=["unidad_medida", "precio_venta"])
        venta = Venta.objects.create(
            cliente=self.cliente, usuario=self.user, medio_pago=self.medio_pago,
            numero_comprobante="V-MONTO", tipo_venta="CONTADO",
        )
        detail = DetalleVenta.objects.create(
            venta=venta, producto=self.producto,
            cantidad=Decimal("2000") / Decimal("5200"),
            precio_unitario=self.producto.precio_venta,
        )
        move = MovimientoInventario.objects.get(tipo="SALIDA")
        self.producto.refresh_from_db()
        self.assertEqual(detail.cantidad, Decimal("0.385"))
        self.assertEqual(detail.subtotal, Decimal("2002.00"))
        self.assertEqual(move.cantidad, detail.cantidad)
        self.assertEqual(self.producto.stock_actual, Decimal("19.615"))

    def test_producto_por_unidad_conserva_cantidad_entera(self):
        unit, _ = UnidadMedida.objects.get_or_create(
            codigo="UND", defaults={"nombre": "Unidad", "simbolo": "unidades", "permite_decimales": False}
        )
        self.producto.nombre = "Natilla 250 g"
        self.producto.unidad_medida = unit
        self.producto.save(update_fields=["nombre", "unidad_medida"])
        response = self.client.post(
            "/api/ventas/", self.venta_payload(detalles=[{
                "producto": self.producto.pk, "cantidad": "2",
                "precio_unitario": "10.00", "descuento": "0.00",
            }]), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(MovimientoInventario.objects.get(tipo="SALIDA").cantidad, Decimal("2.000"))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("18.000"))

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
    def test_numero_comprobante_es_autogenerado_y_unico(self):
        first = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        second = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(
            first.data["numero_comprobante"],
            second.data["numero_comprobante"],
        )
        self.assertRegex(first.data["numero_comprobante"], r"^V-\d{8}-\d{6}$")
        self.assertEqual(Venta.objects.count(), 2)

    def test_usa_estimado_cliente_cuando_no_se_envia_cliente(self):
        payload = self.venta_payload()
        payload.pop("cliente")
        response = self.client.post("/api/ventas/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["cliente_nombre"], "Estimado Cliente")

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
