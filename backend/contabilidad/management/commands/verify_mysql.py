from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from rest_framework.test import APIClient

from finanzas.models import CuentaPorCobrar, CuentaPorPagar
from inventario.models import CategoriaProducto, Producto
from terceros.models import Cliente, MedioPago, Proveedor


class Command(BaseCommand):
    help = "Ejecuta un smoke test HTTP/DRF/ORM/MySQL y revierte todos los datos de prueba."

    def handle(self, *args, **options):
        if connection.vendor != "mysql":
            raise CommandError(f"La base activa es {connection.vendor}, no MySQL.")
        marker = f"SMOKE-{uuid4().hex[:10].upper()}"
        with transaction.atomic():
            group, _ = Group.objects.get_or_create(name="Operaciones")
            user = User.objects.create_user(f"smoke_{marker.lower()}", password=uuid4().hex)
            user.groups.add(group)
            client = APIClient()
            client.force_authenticate(user)
            category = CategoriaProducto.objects.create(nombre=f"Categoría {marker}")
            product = Producto.objects.create(categoria=category, codigo=marker, nombre=f"Producto {marker}", precio_venta=Decimal("1000"), costo_promedio=Decimal("600"), stock_actual=Decimal("20"))
            customer = Cliente.objects.create(nombre=f"Cliente {marker}")
            supplier = Proveedor.objects.create(nombre=f"Proveedor {marker}")
            payment = MedioPago.objects.create(nombre=marker)

            sale = client.post("/api/ventas/", {"cliente": customer.pk, "medio_pago": payment.pk, "tipo_venta": "CREDITO", "descuento": "0.00", "detalles": [{"producto": product.pk, "cantidad": "2.00", "precio_unitario": "1000.00", "descuento": "0.00"}]}, format="json", HTTP_HOST="localhost")
            if sale.status_code != 201:
                raise CommandError(f"Falló venta HTTP: {sale.status_code} {sale.data}")
            purchase = client.post("/api/compras/", {"proveedor": supplier.pk, "numero_factura": marker, "tipo_compra": "CREDITO", "detalles": [{"producto": product.pk, "cantidad": "3.00", "costo_unitario": "650.00"}]}, format="json", HTTP_HOST="localhost")
            if purchase.status_code != 201:
                raise CommandError(f"Falló compra HTTP: {purchase.status_code} {purchase.data}")
            receivable = CuentaPorCobrar.objects.get(venta_id=sale.data["id"])
            payable = CuentaPorPagar.objects.get(compra_id=purchase.data["id"])
            customer_payment = client.post("/api/pagos-clientes/", {"cuenta_por_cobrar": receivable.pk, "medio_pago": payment.pk, "monto": "500.00"}, format="json", HTTP_HOST="localhost")
            supplier_payment = client.post("/api/pagos-proveedores/", {"cuenta_por_pagar": payable.pk, "medio_pago": payment.pk, "monto": "500.00"}, format="json", HTTP_HOST="localhost")
            if customer_payment.status_code != 201 or supplier_payment.status_code != 201:
                raise CommandError("Falló el registro de pagos por API.")
            product.refresh_from_db(); receivable.refresh_from_db(); payable.refresh_from_db()
            if product.stock_actual != Decimal("21.00") or receivable.saldo != Decimal("1500.00") or payable.saldo != Decimal("1450.00"):
                raise CommandError("Los saldos o el inventario no reconciliaron.")
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ventas_venta WHERE id = %s", [sale.data["id"]])
                persisted = cursor.fetchone()[0]
            if persisted != 1:
                raise CommandError("La venta no apareció en la tabla MySQL.")
            self.stdout.write(self.style.SUCCESS(f"MySQL {connection.settings_dict['NAME']}: HTTP→DRF→ORM→tabla verificado; venta, compra, inventario, CxC, CxP y pagos reconciliados."))
            transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS("Datos temporales revertidos correctamente."))
