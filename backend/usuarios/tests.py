from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


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

    def test_perfil_y_cambio_real_de_password(self):
        user = User.objects.create_user("perfil", password="ClaveInicial123!")
        self.client.force_authenticate(user)
        profile = self.client.patch(
            "/api/mi-perfil/",
            {"first_name": "Ana", "correo": "ana@example.com"},
            format="json",
        )
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        changed = self.client.post(
            "/api/cambiar-password/",
            {"actual": "ClaveInicial123!", "nueva": "NuevaClave456!"},
            format="json",
        )
        self.assertEqual(changed.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NuevaClave456!"))

    def test_configuracion_persistente_solo_administrador_modifica(self):
        user = User.objects.create_user("normal", password="ClaveInicial123!")
        self.client.force_authenticate(user)
        self.assertEqual(
            self.client.get("/api/configuracion-empresa/").status_code,
            status.HTTP_200_OK,
        )
        denied = self.client.patch(
            "/api/configuracion-empresa/",
            {"nombre": "Empresa"},
            format="json",
        )
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        user.is_staff = True
        user.save(update_fields=["is_staff"])
        saved = self.client.patch(
            "/api/configuracion-empresa/",
            {"nombre": "Empresa"},
            format="json",
        )
        self.assertEqual(saved.status_code, status.HTTP_200_OK)

    def test_configuracion_visual_es_publica_pero_solo_admin_la_modifica(self):
        public_response = self.client.get("/api/identidad-empresa/")
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertIn("logo", public_response.data)

        denied = self.client.patch(
            "/api/configuracion-empresa/",
            {"nombre": "Cambio anónimo"},
            format="json",
        )
        self.assertEqual(denied.status_code, status.HTTP_401_UNAUTHORIZED)
