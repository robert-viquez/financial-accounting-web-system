from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from config.test_utils import AccountingAPITestCase
from inventario.models import MovimientoInventario, Producto, UnidadMedida


class InventarioAPITests(AccountingAPITestCase):
    def test_genera_codigos_de_categoria_y_producto(self):
        categoria = self.client.post(
            "/api/categorias-producto/",
            {"nombre": "Quesos maduros", "estado": True},
            format="json",
        )
        self.assertEqual(categoria.status_code, status.HTTP_201_CREATED, categoria.data)
        self.assertEqual(categoria.data["codigo"], "QM")
        unidad = UnidadMedida.objects.get(codigo="G")
        producto = self.client.post(
            "/api/productos/",
            {
                "categoria": categoria.data["id"],
                "nombre": "Queso rallado",
                "unidad_medida": unidad.pk,
                "precio_venta": "2500.00",
                "costo_promedio": "1800.00",
                "stock_minimo": "500.00",
                "estado": True,
            },
            format="json",
        )
        self.assertEqual(producto.status_code, status.HTTP_201_CREATED, producto.data)
        self.assertEqual(producto.data["codigo"], "QM-0001")
        self.assertEqual(producto.data["codigo_barras"], "QM-0001")

    def test_lector_registra_entrada_por_codigo_de_barras(self):
        self.producto.codigo_barras = "7501234567890"
        self.producto.save(update_fields=["codigo_barras"])
        response = self.client.post(
            "/api/productos/registrar-entrada/",
            {
                "codigo": "7501234567890",
                "cantidad": "3.00",
                "costo_unitario": "5.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal("23.00"))
        self.assertTrue(
            MovimientoInventario.objects.filter(
                producto=self.producto,
                descripcion="Entrada mediante lector de código de barras",
            ).exists()
        )

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
        # Los filtros se interpretan en la zona horaria de Costa Rica.
        today = timezone.localdate().isoformat()
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
