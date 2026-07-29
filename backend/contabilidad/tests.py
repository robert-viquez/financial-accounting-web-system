from django.test import TestCase

from contabilidad.models import CuentaContable


class CuentaContableTests(TestCase):
    def test_ordenamiento_del_catalogo_para_reportes(self):
        CuentaContable.objects.create(
            codigo="2", nombre="Pasivo", tipo="PASIVO", naturaleza="ACREEDORA"
        )
        CuentaContable.objects.create(
            codigo="1", nombre="Activo", tipo="ACTIVO", naturaleza="DEUDORA"
        )
        self.assertEqual(
            list(CuentaContable.objects.values_list("codigo", flat=True)),
            ["1", "2"],
        )
