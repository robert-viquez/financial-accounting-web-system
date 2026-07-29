from rest_framework import status

from config.test_utils import AccountingAPITestCase


class TercerosTests(AccountingAPITestCase):
    def test_busqueda_y_paginacion_de_clientes(self):
        for index in range(12):
            from terceros.models import Cliente
            Cliente.objects.create(nombre=f"Distribuidor {index:02}")
        response = self.client.get("/api/clientes/?search=Distribuidor&page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 5)
