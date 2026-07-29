from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from inventario.models import CategoriaProducto, Producto
from terceros.models import Cliente, MedioPago, Proveedor


class AccountingAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tester", password="secret123")
        self.client.force_authenticate(self.user)
        self.categoria = CategoriaProducto.objects.create(nombre="Lácteos")
        self.producto = self.crear_producto("P-001", "Queso", "20.00")
        self.producto_2 = self.crear_producto("P-002", "Leche", "15.00")
        self.cliente = Cliente.objects.create(nombre="Cliente Uno")
        self.proveedor = Proveedor.objects.create(nombre="Proveedor Uno")
        self.medio_pago = MedioPago.objects.create(nombre="Efectivo")

    def crear_producto(self, codigo, nombre, stock):
        return Producto.objects.create(
            categoria=self.categoria,
            codigo=codigo,
            nombre=nombre,
            precio_venta=Decimal("10.00"),
            costo_promedio=Decimal("4.00"),
            stock_actual=Decimal(stock),
        )

    def venta_payload(self, numero="V-001", detalles=None, tipo="CONTADO"):
        return {
            "cliente": self.cliente.pk,
            "medio_pago": self.medio_pago.pk,
            "numero_comprobante": numero,
            "tipo_venta": tipo,
            "descuento": "0.00",
            "detalles": detalles or [{
                "producto": self.producto.pk,
                "cantidad": "2.00",
                "precio_unitario": "10.00",
                "descuento": "0.00",
            }],
        }

    def compra_payload(self, numero="C-001", detalles=None, tipo="CONTADO"):
        return {
            "proveedor": self.proveedor.pk,
            "numero_factura": numero,
            "tipo_compra": tipo,
            "detalles": detalles or [{
                "producto": self.producto.pk,
                "cantidad": "2.00",
                "costo_unitario": "5.00",
            }],
        }
