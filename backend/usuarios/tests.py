from rest_framework import status
from rest_framework.test import APITestCase


class AutenticacionTests(APITestCase):
    def test_endpoint_protegido_rechaza_usuario_anonimo(self):
        response = self.client.get("/api/productos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalido_no_emite_token(self):
        response = self.client.post(
            "/api/token/", {"username": "nadie", "password": "incorrecta"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
