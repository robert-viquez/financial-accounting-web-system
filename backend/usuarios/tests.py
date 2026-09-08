from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group, Permission, User

from .models import ConfiguracionEmpresa


class ConfiguracionInicialTests(APITestCase):
    endpoint = "/api/setup/admin/"

    def test_base_fresca_requiere_configuracion(self):
        response = self.client.get("/api/setup/status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"setup_required": True})

    def test_superusuario_activo_completa_configuracion(self):
        User.objects.create_superuser("existente", password="ClaveSegura123!")
        response = self.client.get("/api/setup/status/")
        self.assertEqual(response.data, {"setup_required": False})

    def test_usuario_normal_no_desactiva_configuracion_inicial(self):
        User.objects.create_user("normal", password="ClaveSegura123!")
        response = self.client.get("/api/setup/status/")
        self.assertEqual(response.data, {"setup_required": True})

    def test_crea_primer_administrador_y_bloquea_el_segundo(self):
        payload = {
            "username": "admin-inicial",
            "email": "admin@example.com",
            "password": "ClaveSegura123!",
            "password_confirm": "ClaveSegura123!",
        }
        created = self.client.post(self.endpoint, payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="admin-inicial")
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(payload["password"]))

        rejected = self.client.post(
            self.endpoint,
            {**payload, "username": "otro-admin", "email": "otro@example.com"},
            format="json",
        )
        self.assertEqual(rejected.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username="otro-admin").exists())

    def test_rechaza_password_invalido(self):
        weak = self.client.post(
            self.endpoint,
            {
                "username": "admin",
                "password": "123",
                "password_confirm": "123",
            },
            format="json",
        )
        self.assertEqual(weak.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.exists())


class AutenticacionTests(APITestCase):
    def test_perfil_valida_y_persiste_locale_sin_escalar_privilegios(self):
        user = User.objects.create_user("locale-user", password="ClaveInicial123!")
        self.client.force_authenticate(user)
        saved = self.client.patch(
            "/api/mi-perfil/", {"locale": "en", "is_staff": True}, format="json"
        )
        self.assertEqual(saved.status_code, status.HTTP_200_OK)
        self.assertEqual(saved.data["locale"], "en")
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertEqual(user.preferencias.locale, "en")

        invalid = self.client.patch("/api/mi-perfil/", {"locale": "fr"}, format="json")
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

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
        configuracion = ConfiguracionEmpresa.objects.create(
            pk=1,
            nombre="Empresa original",
            lector_codigo_barras=True,
        )
        user = User.objects.create_user("normal", password="ClaveInicial123!")
        self.client.force_authenticate(user)
        self.assertEqual(
            self.client.get("/api/configuracion-empresa/").status_code,
            status.HTTP_200_OK,
        )
        denied = self.client.patch(
            "/api/configuracion-empresa/",
            {"nombre": "Cambio no autorizado", "lector_codigo_barras": False},
            format="json",
        )
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        configuracion.refresh_from_db()
        self.assertEqual(configuracion.nombre, "Empresa original")
        self.assertTrue(configuracion.lector_codigo_barras)

        user.is_staff = True
        user.save(update_fields=["is_staff"])
        saved = self.client.patch(
            "/api/configuracion-empresa/",
            {"lector_codigo_barras": False},
            format="json",
        )
        self.assertEqual(saved.status_code, status.HTTP_200_OK)
        self.assertFalse(saved.data["lector_codigo_barras"])

        reloaded = self.client.get("/api/configuracion-empresa/")
        self.assertEqual(reloaded.status_code, status.HTTP_200_OK)
        self.assertFalse(reloaded.data["lector_codigo_barras"])
        configuracion.refresh_from_db()
        self.assertFalse(configuracion.lector_codigo_barras)

    def test_locale_global_solo_administrador_modifica_y_valida(self):
        normal = User.objects.create_user("locale-normal", password="ClaveInicial123!")
        admin = User.objects.create_user("locale-admin", password="ClaveInicial123!", is_staff=True)
        self.client.force_authenticate(normal)
        denied = self.client.patch(
            "/api/configuracion-empresa/", {"locale_predeterminado": "en"}, format="json"
        )
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(admin)
        saved = self.client.patch(
            "/api/configuracion-empresa/", {"locale_predeterminado": "en"}, format="json"
        )
        self.assertEqual(saved.status_code, status.HTTP_200_OK)
        self.assertEqual(saved.data["locale_predeterminado"], "en")
        invalid = self.client.patch(
            "/api/configuracion-empresa/", {"locale_predeterminado": "fr"}, format="json"
        )
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

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


class AdministracionUsuariosTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user("staff", password="ClaveInicial123!", is_staff=True)
        self.superuser = User.objects.create_superuser("root", password="ClaveInicial123!")
        self.normal = User.objects.create_user("normal", password="ClaveInicial123!")

    def test_no_administrador_no_puede_gestionar_usuarios(self):
        self.client.force_authenticate(self.normal)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.client.post("/api/usuarios/", {"username": "nuevo", "password": "ClaveNueva123!"}).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_lista_crea_desactiva_y_restablece_password(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, status.HTTP_200_OK)
        created = self.client.post(
            "/api/usuarios/",
            {"username": "nuevo", "first_name": "Nuevo", "password": "ClaveNueva123!"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        user_id = created.data["id"]
        changed = self.client.patch(f"/api/usuarios/{user_id}/", {"is_active": False}, format="json")
        self.assertEqual(changed.status_code, status.HTTP_200_OK)
        self.assertFalse(changed.data["is_active"])
        reset = self.client.post(
            f"/api/usuarios/{user_id}/password/", {"password": "OtraClave456!"}, format="json"
        )
        self.assertEqual(reset.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(pk=user_id).check_password("OtraClave456!"))

    def test_validacion_password_se_aplica(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(
            "/api/usuarios/", {"username": "inseguro", "password": "123"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_no_puede_escalar_ni_modificar_superusuario(self):
        self.client.force_authenticate(self.staff)
        escalated = self.client.patch(
            f"/api/usuarios/{self.staff.pk}/", {"is_staff": False, "is_superuser": True}, format="json"
        )
        self.assertEqual(escalated.status_code, status.HTTP_400_BAD_REQUEST)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_staff)
        self.assertFalse(self.staff.is_superuser)
        denied = self.client.patch(
            f"/api/usuarios/{self.superuser.pk}/", {"first_name": "Cambio"}, format="json"
        )
        self.assertEqual(denied.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            self.client.delete(f"/api/usuarios/{self.superuser.pk}/").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.patch(
                f"/api/usuarios/{self.staff.pk}/", {"is_active": False}, format="json"
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_perfil_no_permite_autoasignar_roles(self):
        role = Group.objects.create(name="Privilegiado")
        self.client.force_authenticate(self.normal)
        response = self.client.patch(
            "/api/mi-perfil/", {"roles": [role.name], "is_staff": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal.refresh_from_db()
        self.assertFalse(self.normal.is_staff)
        self.assertFalse(self.normal.groups.exists())

    def test_superusuario_puede_cambiar_estado_staff_pero_no_superuser(self):
        self.client.force_authenticate(self.superuser)
        promoted = self.client.patch(
            f"/api/usuarios/{self.normal.pk}/", {"is_staff": True}, format="json"
        )
        self.assertEqual(promoted.status_code, status.HTTP_200_OK)
        self.assertTrue(promoted.data["is_staff"])
        self.assertTrue(self.superuser.is_superuser)


class AdministracionRolesTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user("staff-roles", password="ClaveInicial123!", is_staff=True)
        self.normal = User.objects.create_user("normal-roles", password="ClaveInicial123!")
        self.permission = Permission.objects.filter(content_type__app_label="inventario").first()

    def test_staff_crea_actualiza_permisos_y_elimina_rol_sin_uso(self):
        self.client.force_authenticate(self.staff)
        created = self.client.post(
            "/api/roles/", {"name": "Bodega temporal", "permisos": [self.permission.pk]}, format="json"
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        role_id = created.data["id"]
        self.assertEqual(created.data["permisos"], [self.permission.pk])
        updated = self.client.patch(f"/api/roles/{role_id}/", {"name": "Bodega", "permisos": []}, format="json")
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["permisos"], [])
        self.assertEqual(self.client.delete(f"/api/roles/{role_id}/").status_code, status.HTTP_204_NO_CONTENT)

    def test_rol_en_uso_no_se_elimina_y_no_admin_no_gestiona(self):
        role = Group.objects.create(name="Ventas temporal")
        self.normal.groups.add(role)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.delete(f"/api/roles/{role.pk}/").status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.normal)
        self.assertEqual(self.client.get("/api/roles/").status_code, status.HTTP_403_FORBIDDEN)

    def test_no_se_pueden_asignar_permisos_tecnicos_a_roles(self):
        permiso_auth = Permission.objects.filter(content_type__app_label="auth").first()
        self.client.force_authenticate(self.staff)
        response = self.client.post(
            "/api/roles/", {"name": "Escalado", "permisos": [permiso_auth.pk]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
