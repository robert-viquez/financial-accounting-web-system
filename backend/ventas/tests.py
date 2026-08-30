from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status

from config.test_utils import AccountingAPITestCase
from inventario.models import MovimientoInventario, UnidadMedida
from contabilidad.models import AsientoContable
from ventas.models import ComprobanteElectronico, DetalleVenta, Venta
from ventas.services import FacturacionElectronicaService


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


class ComprobanteElectronicoModelTests(AccountingAPITestCase):
    def setUp(self):
        super().setUp()
        response = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.venta = Venta.objects.get(pk=response.data["id"])

    def comprobante(self, **kwargs):
        datos = {
            "venta": self.venta,
            "tipo_comprobante": ComprobanteElectronico.TipoComprobante.FACTURA_ELECTRONICA,
        }
        datos.update(kwargs)
        return ComprobanteElectronico(**datos)

    def test_crea_borrador_asociado_a_venta(self):
        comprobante = self.comprobante()
        comprobante.full_clean()
        comprobante.save()
        self.assertEqual(comprobante.estado_hacienda, "BORRADOR")
        self.assertEqual(self.venta.comprobantes_electronicos.get(), comprobante)

    def test_acepta_clave_numerica_de_50_digitos(self):
        comprobante = self.comprobante(clave_numerica="1" * 50)
        comprobante.full_clean()

    def test_rechaza_clave_con_longitud_incorrecta(self):
        with self.assertRaises(ValidationError):
            self.comprobante(clave_numerica="1" * 49).full_clean()

    def test_rechaza_clave_con_caracteres_no_numericos(self):
        with self.assertRaises(ValidationError):
            self.comprobante(clave_numerica=("1" * 49) + "A").full_clean()

    def test_rechaza_clave_duplicada(self):
        clave = "2" * 50
        primero = self.comprobante(clave_numerica=clave)
        primero.full_clean()
        primero.save()
        with self.assertRaises(ValidationError):
            self.comprobante(clave_numerica=clave).full_clean()

    def test_rechaza_fecha_respuesta_anterior_al_envio(self):
        envio = timezone.now()
        with self.assertRaises(ValidationError):
            self.comprobante(
                fecha_envio=envio,
                fecha_respuesta=envio - timedelta(seconds=1),
            ).full_clean()


class FacturacionElectronicaServiceTests(AccountingAPITestCase):
    def setUp(self):
        super().setUp()
        response = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        self.venta = Venta.objects.get(pk=response.data["id"])

    def test_preparar_crea_borrador_sin_efectos_en_venta_inventario_o_contabilidad(self):
        self.producto.refresh_from_db()
        stock = self.producto.stock_actual
        movimientos = MovimientoInventario.objects.count()
        asientos = AsientoContable.objects.count()
        datos_venta = (self.venta.total, self.venta.numero_comprobante, self.venta.estado)

        comprobante = FacturacionElectronicaService.preparar_comprobante(
            self.venta, ComprobanteElectronico.TipoComprobante.FACTURA_ELECTRONICA
        )

        self.venta.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(comprobante.estado_hacienda, "BORRADOR")
        self.assertIsNone(comprobante.clave_numerica)
        self.assertIsNone(comprobante.xml_generado)
        self.assertEqual(
            (self.venta.total, self.venta.numero_comprobante, self.venta.estado),
            datos_venta,
        )
        self.assertEqual(self.producto.stock_actual, stock)
        self.assertEqual(MovimientoInventario.objects.count(), movimientos)
        self.assertEqual(AsientoContable.objects.count(), asientos)

    def test_validacion_identifica_informacion_fiscal_faltante(self):
        resultado = FacturacionElectronicaService.validar_datos_preparacion(self.venta)
        self.assertFalse(resultado["preparado"])
        self.assertIn("identificacion_cliente", resultado["faltantes"])


class ComprobanteElectronicoAPITests(AccountingAPITestCase):
    def setUp(self):
        super().setUp()
        response = self.client.post("/api/ventas/", self.venta_payload(), format="json")
        self.venta = Venta.objects.get(pk=response.data["id"])
        self.preparar_url = (
            f"/api/ventas/{self.venta.pk}/comprobante-electronico/preparar/"
        )

    def test_preparar_requiere_autenticacion(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.preparar_url, {"tipo_comprobante": "FACTURA_ELECTRONICA"}, format="json"
        )
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_prepara_y_retorna_borrador(self):
        response = self.client.post(
            self.preparar_url, {"tipo_comprobante": "FACTURA_ELECTRONICA"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["venta"], self.venta.pk)
        self.assertEqual(response.data["numero_comprobante_venta"], self.venta.numero_comprobante)
        self.assertEqual(response.data["estado_hacienda"], "BORRADOR")
        self.assertIsNone(response.data["clave_numerica"])
        self.assertIn("validacion_preparacion", response.data)

    def test_consulta_comprobantes_de_la_venta(self):
        FacturacionElectronicaService.preparar_comprobante(
            self.venta, ComprobanteElectronico.TipoComprobante.TIQUETE_ELECTRONICO
        )
        response = self.client.get(
            f"/api/ventas/{self.venta.pk}/comprobantes-electronicos/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["tipo_comprobante"], "TIQUETE_ELECTRONICO")

    def test_venta_inexistente_retorna_404(self):
        response = self.client.post(
            "/api/ventas/999999/comprobante-electronico/preparar/",
            {"tipo_comprobante": "FACTURA_ELECTRONICA"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
