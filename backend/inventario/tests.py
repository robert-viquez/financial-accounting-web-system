from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from config.test_utils import AccountingAPITestCase
from inventario.models import MovimientoInventario, Producto


class InventarioAPITests(AccountingAPITestCase):
    def test_productos_estan_paginados_y_page_size_tiene_limite(self):
        for index in range(105):
            self.crear_producto(f"X-{index:03}", f"Producto {index:03}", "1.00")
        response = self.client.get("/api/productos/?page_size=500")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 107)
        self.assertEqual(len(response.data["results"]), 100)

    def test_reporte_de_movimientos_filtra_producto_tipo_y_fecha(self):
        MovimientoInventario.objects.create(
            producto=self.producto, tipo="ENTRADA", cantidad="2.00",
            descripcion="Entrada de prueba",
        )
        MovimientoInventario.objects.create(
            producto=self.producto_2, tipo="SALIDA", cantidad="1.00",
            descripcion="Salida de prueba",
        )
        today = timezone.now().date().isoformat()
        response = self.client.get(
            f"/api/movimientos-inventario/?producto={self.producto.pk}"
            f"&tipo=ENTRADA&fecha_desde={today}&fecha_hasta={today}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["descripcion"], "Entrada de prueba")

    def test_movimientos_son_solo_lectura(self):
        response = self.client.post("/api/movimientos-inventario/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
