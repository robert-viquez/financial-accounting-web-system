"""Dataset ficticio y reproducible para la demostración de ByteForge Technologies."""
import os
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from compras.models import Compra, DetalleCompra
from contabilidad.models import AsientoContable, DetalleAsiento, PeriodoContable
from contabilidad.services import ContabilidadService
from finanzas.models import CuentaPorCobrar, CuentaPorPagar, PagoCliente, PagoProveedor
from inventario.models import CategoriaProducto, MovimientoInventario, Producto, UnidadMedida
from inventario.quantities import normalize_quantity
from terceros.models import Cliente, MedioPago, Proveedor
from usuarios.models import ConfiguracionEmpresa, RegistroAuditoria
from ventas.models import DetalleVenta, SecuenciaComprobanteVenta, Venta

CENT = Decimal("0.01")
START, END = date(2026, 6, 1), date(2026, 8, 25)
PRODUCTS = [
    ("CPU-001", "AMD Ryzen 7 9700X", "245000", "198000", 3, 5, "UND", "Procesadores"),
    ("CPU-002", "Intel Core Ultra 7 265K", "265000", "218000", 3, 4, "UND", "Procesadores"),
    ("GPU-001", "Tarjeta gráfica GeForce RTX 5070 12 GB", "455000", "389000", 2, 5, "UND", "Tarjetas gráficas"),
    ("GPU-002", "Tarjeta gráfica Radeon RX 9070 16 GB", "429000", "365000", 2, 4, "UND", "Tarjetas gráficas"),
    ("MB-001", "Tarjeta madre ATX Wi-Fi 7", "159000", "126000", 3, 4, "UND", "Tarjetas madre"),
    ("RAM-001", "Kit de memoria 32 GB DDR5-6000", "72000", "55000", 5, 7, "UND", "Memoria"),
    ("SSD-001", "SSD NVMe PCIe 4.0 de 2 TB", "89000", "68000", 5, 8, "UND", "Almacenamiento"),
    ("PSU-001", "Fuente modular 850 W 80 Plus Gold", "93000", "71000", 3, 4, "UND", "Fuentes de poder"),
    ("CASE-001", "Gabinete ATX de flujo optimizado", "64000", "47000", 3, 4, "UND", "Gabinetes"),
    ("COOL-001", "Enfriamiento líquido AIO 240 mm", "69000", "52000", 3, 3, "UND", "Enfriamiento"),
    ("MON-001", "Monitor IPS 27 pulgadas QHD 165 Hz", "189000", "148000", 3, 6, "UND", "Monitores"),
    ("KEY-001", "Teclado mecánico inalámbrico", "59000", "41000", 4, 6, "UND", "Teclados"),
    ("MOU-001", "Mouse ergonómico para juegos", "36000", "24000", 5, 7, "UND", "Mouse"),
    ("LAP-001", "Laptop empresarial 14 pulgadas", "575000", "487000", 2, 4, "UND", "Laptops"),
    ("PHN-001", "Smartphone Android 5G 256 GB", "329000", "274000", 3, 5, "UND", "Smartphones"),
    ("TAB-001", "Tablet de 11 pulgadas 128 GB", "249000", "201000", 3, 4, "UND", "Tablets"),
    ("NET-001", "Router Wi-Fi 7 de doble banda", "119000", "89000", 3, 5, "UND", "Redes"),
    ("NET-002", "Switch administrable Gigabit de 8 puertos", "49000", "34000", 4, 4, "UND", "Redes"),
    ("ACC-001", "Dock USB-C de 10 puertos", "54000", "38000", 5, 6, "UND", "Accesorios"),
    ("ACC-002", "Webcam Full HD con micrófono", "31000", "21000", 5, 5, "UND", "Accesorios"),
]
CUSTOMERS = [
    "Estudio Vector S.R.L.", "Café Circuito S.A.", "Nube Clara Consultores",
    "Laboratorio Prisma S.R.L.", "Taller Horizonte Digital", "Academia Código Norte",
    "Arquitectura Módulo S.A.", "Punto Cero Diseño", "Logística Faro S.R.L.",
    "Clínica Nova Salud", "Editorial Píxel S.A.", "Hotel Sendero Azul",
    "Ingeniería Delta S.R.L.", "Cooperativa Valle Digital", "Servicios Órbita S.A.",
]
SUPPLIERS = [
    ("Silicon Ridge Distribution S.A.", 30, "ventas@siliconridge.test"),
    ("Nova Components S.R.L.", 15, "pedidos@novacomponents.test"),
    ("Pacific Device Wholesale S.A.", 30, "cuentas@pacificdevice.test"),
    ("Vertex Networking S.R.L.", 15, "ventas@vertexnetworking.test"),
    ("Display Harbor Imports S.A.", 30, "facturacion@displayharbor.test"),
    ("CoreLink Accessories S.R.L.", 30, "operaciones@corelink.test"),
]


class Command(BaseCommand):
    help = "Reconstruye y valida la base demo ficticia de ByteForge Technologies."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")
        parser.add_argument("--seed", type=int, default=20260828)

    def handle(self, *args, **opts):
        self._safety(opts["reset"])
        password = os.getenv("DEMO_PASSWORD")
        if not password:
            raise CommandError("Defina DEMO_PASSWORD; la contraseña demo no se guarda en el repositorio.")
        with transaction.atomic():
            if opts["reset"]:
                self._reset()
            elif Venta.objects.exists() or Compra.objects.exists():
                raise CommandError("Ya existen transacciones. Use --reset para evitar duplicados.")
            rng = random.Random(opts["seed"])
            ctx = self._masters(password)
            self._periods()
            self._initial_stock(ctx)
            purchases = self._purchases(rng, ctx)
            sales = self._sales(rng, ctx)
            self._payments(ctx, purchases, sales)
            metrics = self._validate(opts["seed"])
            PeriodoContable.objects.filter(fecha_inicio__in=[date(2026, 6, 1), date(2026, 7, 1)]).update(cerrado=True)
            self._summary(metrics)

    @staticmethod
    def _safety(reset):
        allowed = os.getenv("ALLOW_DEMO_SEED", "").lower() in {"1", "true", "yes", "on"}
        if not allowed:
            action = "El borrado" if reset else "El seed"
            raise CommandError(f"{action} fue cancelado: requiere ALLOW_DEMO_SEED=true. No se modificó ningún dato.")
        if END > timezone.localdate():
            raise CommandError(f"El periodo termina en {END}; no se permiten fechas futuras.")

    @staticmethod
    def _reset():
        # Orden explícito para respetar los PROTECT; se preservan catálogos, roles y configuración.
        for model in (DetalleAsiento, AsientoContable, PagoCliente, PagoProveedor,
                      CuentaPorCobrar, CuentaPorPagar, DetalleVenta, DetalleCompra,
                      Venta, Compra, MovimientoInventario, SecuenciaComprobanteVenta,
                      Producto, Cliente, Proveedor, RegistroAuditoria, PeriodoContable,
                      CategoriaProducto, ConfiguracionEmpresa):
            model.objects.all().delete()
        User.objects.all().delete()

    @staticmethod
    def _masters(password):
        roles = {
            name: Group.objects.get_or_create(name=name)[0]
            for name in ["Ventas", "Inventario", "Contabilidad", "Gerencia", "Operaciones"]
        }
        permisos_por_rol = {
            "Ventas": ["ventas", "terceros"],
            "Inventario": ["inventario"],
            "Contabilidad": ["contabilidad", "finanzas"],
            "Gerencia": ["ventas", "compras", "inventario", "contabilidad", "finanzas"],
            "Operaciones": ["ventas", "compras", "inventario", "terceros", "finanzas"],
        }
        for nombre, aplicaciones in permisos_por_rol.items():
            roles[nombre].permissions.set(
                Permission.objects.filter(content_type__app_label__in=aplicaciones)
            )
        username = os.getenv("DEMO_USERNAME", "demo").strip() or "demo"
        demo = User.objects.create_user(
            username, email="demo@byteforge.test", password=password,
            first_name="Usuario", last_name="Demo", is_active=True,
        )
        demo.groups.add(roles["Operaciones"])
        ConfiguracionEmpresa.objects.update_or_create(pk=1, defaults={
            "nombre": "ByteForge Technologies",
            "identificacion": "FICTICIA-DEMO-001",
            "telefono": "0000-0000",
            "correo": "contacto@byteforge.test",
            "direccion": "Dirección ficticia para demostración, Costa Rica",
            "iva": Decimal("13.00"), "moneda": "CRC",
            "lector_codigo_barras": True, "prefijo_productos": "BF",
        })
        unit, _ = UnidadMedida.objects.update_or_create(
            codigo="UND", defaults={"nombre": "Unidad", "simbolo": "unidades", "permite_decimales": False, "estado": True})
        categories = {
            name: CategoriaProducto.objects.create(
                nombre=name, descripcion=f"Catálogo ficticio de {name.lower()} para la demostración."
            )
            for name in dict.fromkeys(spec[7] for spec in PRODUCTS)
        }
        products = [Producto.objects.create(
            codigo=code, nombre=name, categoria=categories[category], unidad_medida=unit,
            precio_venta=Decimal(price), costo_promedio=Decimal(cost),
            stock_minimo=Decimal(minimum), stock_actual=0,
            descripcion="Producto de tecnología ficticio para venta minorista.")
            for code, name, price, cost, minimum, _, _, category in PRODUCTS]
        generic_customer = Cliente.objects.create(
            nombre="Estimado Cliente", identificacion="CF-000000001",
            telefono="", correo=None, direccion="Dirección ficticia, Costa Rica", dias_credito=0)
        customers = [Cliente.objects.create(
            nombre=name, identificacion=f"FIC-CLI-{i:04d}", telefono=f"0000-{i:04d}",
            correo=f"compras{i}@cliente.test", direccion="Dirección ficticia, Costa Rica",
            dias_credito=30) for i, name in enumerate(CUSTOMERS, 1)]
        suppliers = [Proveedor.objects.create(
            nombre=name, identificacion=f"FIC-PRV-{i:04d}", telefono=f"0001-{i:04d}",
            correo=email, direccion="Dirección ficticia, Costa Rica",
            dias_credito=days) for i, (name, days, email) in enumerate(SUPPLIERS, 1)]
        methods = {}
        aliases = {"Efectivo": ("efectivo",), "SINPE": ("sinpe", "transferencia"),
                   "Datáfono": ("datáfono", "datafono", "tarjeta")}
        existing = list(MedioPago.objects.all())
        for name, accepted in aliases.items():
            method = next((m for m in existing if m.nombre.lower() in accepted), None)
            if method is None:
                method = MedioPago.objects.create(nombre=name)
            methods[name] = method
        ContabilidadService.asegurar_catalogo_base()
        return {"admin": demo, "cashier": demo, "products": products,
                "generic_customer": generic_customer,
                "customers": customers, "suppliers": suppliers, "methods": methods}

    @staticmethod
    def _periods():
        for name, start, end in (
            ("Junio 2026", date(2026, 6, 1), date(2026, 6, 30)),
            ("Julio 2026", date(2026, 7, 1), date(2026, 7, 31)),
            ("Agosto 2026", date(2026, 8, 1), date(2026, 8, 31)),
        ):
            period = PeriodoContable(nombre=name, fecha_inicio=start, fecha_fin=end, cerrado=False)
            period.full_clean()
            period.save()

    @staticmethod
    def _moment(day, rng=None):
        return timezone.make_aware(datetime.combine(day, time(
            rng.randint(9, 17) if rng else 8,
            rng.choice([3, 11, 18, 27, 36, 44, 52]) if rng else 0)))

    @staticmethod
    def _dates(first, last):
        return [first + timedelta(days=i) for i in range((last - first).days + 1)]

    def _initial_stock(self, ctx):
        moment = self._moment(START - timedelta(days=3))
        for product, spec in zip(ctx["products"], PRODUCTS):
            quantity = (Decimal(18 + spec[5] * 3) + Decimal("0.750")
                        if spec[6] == "KG" else Decimal(22 + spec[5] * 4))
            product.stock_actual = quantity
            product.save(update_fields=["stock_actual"])
            move = MovimientoInventario.objects.create(
                producto=product, tipo="ENTRADA", cantidad=quantity,
                costo_unitario=product.costo_promedio,
                descripcion="Inventario inicial de productos terminados", usuario=ctx["admin"])
            MovimientoInventario.objects.filter(pk=move.pk).update(fecha=moment)

    def _purchases(self, rng, ctx):
        days = sorted(rng.sample(self._dates(START, END - timedelta(days=5)), 18))
        weighted = [p for p, spec in zip(ctx["products"], PRODUCTS) for _ in range(spec[5])]
        credit = set(rng.sample(range(18), 12))
        result = []
        for i, day in enumerate(days):
            purchase = Compra.objects.create(
                proveedor=ctx["suppliers"][i % 6], usuario=ctx["admin"],
                numero_factura=f"COM-2026-{i + 1:04d}",
                tipo_compra="CREDITO" if i in credit else "CONTADO",
                observaciones="Reposición ordinaria de inventario")
            selected = list(dict.fromkeys(rng.sample(weighted, rng.randint(4, 7))))
            while len(selected) < 3:
                candidate = rng.choice(ctx["products"])
                if candidate not in selected:
                    selected.append(candidate)
            for product in selected:
                base = next(Decimal(row[3]) for row in PRODUCTS if row[0] == product.codigo)
                cost = (base * Decimal(rng.choice(["0.98", "0.99", "1", "1.01", "1.02"]))).quantize(CENT)
                quantity = (Decimal(rng.choice([
                    "6.750", "11.600", "12.000", "15.500", "18.450", "20.000", "22.750"
                ])) if product.unidad_medida.codigo == "KG" else Decimal(rng.randint(4, 9)))
                DetalleCompra.objects.create(compra=purchase, producto=product,
                    cantidad=quantity, costo_unitario=cost)
            moment = self._moment(day, rng)
            Compra.objects.filter(pk=purchase.pk).update(fecha=moment)
            MovimientoInventario.objects.filter(descripcion__endswith=purchase.numero_factura).update(fecha=moment)
            AsientoContable.objects.filter(origen="COMPRA", referencia=str(purchase.pk)).update(fecha=day)
            if purchase.tipo_compra == "CREDITO":
                account = CuentaPorPagar.objects.get(compra=purchase)
                CuentaPorPagar.objects.filter(pk=account.pk).update(
                    fecha_emision=day, fecha_vencimiento=day + timedelta(days=purchase.proveedor.dias_credito))
            purchase.refresh_from_db()
            result.append(purchase)
        return result

    def _sales(self, rng, ctx):
        days, pool = [], self._dates(START, END)
        weights = [1 if d.month == 6 else 2 if d.month == 7 else 4 for d in pool]
        while len(days) < 66:
            day = rng.choices(pool, weights=weights, k=1)[0]
            if days.count(day) < 4:
                days.append(day)
        days.sort()
        weighted = [p for p, spec in zip(ctx["products"], PRODUCTS) for _ in range(spec[5])]
        credit = set(rng.sample(range(8, 61), 3))
        payment_names = rng.choices(["SINPE", "Efectivo", "Datáfono"], weights=[40, 35, 25], k=66)
        result = []
        individual_cash_sales = {2, 45}
        for i, day in enumerate(days):
            customer = (ctx["customers"][(i * 7) % len(ctx["customers"])]
                        if i in credit or i in individual_cash_sales else ctx["generic_customer"])
            sale = Venta.objects.create(
                cliente=customer, usuario=ctx["cashier"],
                medio_pago=ctx["methods"][payment_names[i]], numero_comprobante=f"VTA-2026-{i + 1:04d}",
                tipo_venta="CREDITO" if i in credit else "CONTADO",
                observaciones="Venta minorista de productos terminados")
            count = rng.choices([1, 2, 3, 4], weights=[30, 38, 25, 7], k=1)[0]
            selected = []
            while len(selected) < count:
                product = rng.choice(weighted)
                if product not in selected and product.stock_actual >= Decimal("0.225"):
                    selected.append(product)
            running = Decimal(0)
            amount_requested = []
            for product in selected:
                if product.unidad_medida.codigo == "KG":
                    if rng.random() < .42:
                        target = Decimal(rng.choice(["1000", "1500", "1800", "2000", "2300", "2500", "3000", "3500", "4000", "5000"]))
                        qty = normalize_quantity(target / product.precio_venta)
                        amount_requested.append(f"₡{target}")
                    else:
                        qty = Decimal(rng.choice(["0.225", "0.350", "0.475", "0.650", "0.825", "1.000", "1.250"]))
                else:
                    qty = Decimal(2 if rng.random() < .18 else 1)
                if product.stock_actual < qty or running + product.precio_venta * qty > Decimal(900000):
                    qty = Decimal(1)
                DetalleVenta.objects.create(venta=sale, producto=product, cantidad=qty,
                    precio_unitario=product.precio_venta, descuento=0)
                running += product.precio_venta * qty
            if amount_requested:
                Venta.objects.filter(pk=sale.pk).update(
                    observaciones="Venta minorista; peso calculado desde monto solicitado " + ", ".join(amount_requested)
                )
            moment = self._moment(day, rng)
            Venta.objects.filter(pk=sale.pk).update(fecha=moment)
            MovimientoInventario.objects.filter(descripcion__endswith=sale.numero_comprobante).update(fecha=moment)
            AsientoContable.objects.filter(origen="VENTA", referencia=str(sale.pk)).update(fecha=day)
            if sale.tipo_venta == "CREDITO":
                account = CuentaPorCobrar.objects.get(venta=sale)
                CuentaPorCobrar.objects.filter(pk=account.pk).update(
                    fecha_emision=day, fecha_vencimiento=day + timedelta(days=sale.cliente.dias_credito))
            sale.refresh_from_db()
            result.append(sale)
        return result

    def _payments(self, ctx, purchases, sales):
        method = ctx["methods"]["SINPE"]
        credits = [p for p in purchases if p.tipo_compra == "CREDITO"]
        for i, purchase in enumerate(credits[:7]):
            account = CuentaPorPagar.objects.get(compra=purchase)
            amounts = [account.saldo] if i < 4 else [account.saldo * Decimal(".25"), account.saldo * Decimal(".20")]
            for part, raw in enumerate(amounts, 1):
                account.refresh_from_db()
                payment = PagoProveedor.objects.create(
                    cuenta_por_pagar=account, medio_pago=method,
                    monto=min(raw.quantize(CENT), account.saldo),
                    referencia=f"PAG-2026-{i + 1:02d}-{part}", usuario=ctx["admin"])
                day = min(purchase.fecha.date() + timedelta(days=8 + part * 4), END)
                PagoProveedor.objects.filter(pk=payment.pk).update(fecha=self._moment(day))
                AsientoContable.objects.filter(origen="PAGO", referencia=str(payment.pk)).update(fecha=day)
        credits = [s for s in sales if s.tipo_venta == "CREDITO"]
        for i, sale in enumerate(credits[:2]):
            account = CuentaPorCobrar.objects.get(venta=sale)
            amount = account.saldo if i == 0 else (account.saldo * Decimal(".50")).quantize(CENT)
            payment = PagoCliente.objects.create(cuenta_por_cobrar=account, medio_pago=method,
                monto=amount, referencia=f"REC-2026-{i + 1:02d}", usuario=ctx["cashier"])
            day = min(sale.fecha.date() + timedelta(days=12), END)
            PagoCliente.objects.filter(pk=payment.pk).update(fecha=self._moment(day))
            AsientoContable.objects.filter(origen="COBRO", referencia=str(payment.pk)).update(fecha=day)

    @staticmethod
    def _movement_effect(move):
        if move.tipo == "ENTRADA":
            return move.cantidad
        if move.tipo == "SALIDA":
            return -move.cantidad
        description = move.descripcion or ""
        if description.startswith("Reversión de venta"):
            return move.cantidad
        if description.startswith("Reversión de compra"):
            return -move.cantidad
        return move.cantidad

    def _inventory_diagnostics(self):
        """Validate document quantities and reconstruct stock from movements."""
        expected_by_document = {}
        for detail in DetalleCompra.objects.select_related("compra"):
            key = (f"Entrada por compra {detail.compra.numero_factura}", detail.producto_id)
            expected_by_document[key] = expected_by_document.get(key, Decimal("0")) + detail.cantidad
        for detail in DetalleVenta.objects.select_related("venta"):
            key = (f"Salida por venta {detail.venta.numero_comprobante}", detail.producto_id)
            expected_by_document[key] = expected_by_document.get(key, Decimal("0")) + detail.cantidad

        inconsistencies = 0
        products = Producto.objects.select_related("unidad_medida").prefetch_related("movimientos")
        for product in products:
            moves = list(product.movimientos.all())
            for move in moves:
                key = (move.descripcion or "", product.pk)
                expected_quantity = expected_by_document.get(key)
                if expected_quantity is None or move.cantidad == expected_quantity:
                    continue
                inconsistencies += 1
                self.stdout.write(
                    "\nINCONSISTENCIA DE MOVIMIENTO\n"
                    f"Producto: {product.codigo} — {product.nombre}\n"
                    f"Unidad de medida: {product.unidad_medida.codigo} ({product.unidad_medida.simbolo})\n"
                    f"Movimiento ID: {move.pk}\nTipo: {move.tipo}\n"
                    f"Documento origen: {move.descripcion}\n"
                    f"Cantidad almacenada: {move.cantidad}\nCantidad esperada: {expected_quantity}\n"
                    f"Diferencia: {move.cantidad - expected_quantity}\nFecha: {move.fecha}\n"
                )

            initial = sum((m.cantidad for m in moves
                           if m.tipo == "ENTRADA" and m.descripcion == "Inventario inicial de productos terminados"),
                          Decimal("0"))
            entries = sum((m.cantidad for m in moves
                           if m.tipo == "ENTRADA" and m.descripcion != "Inventario inicial de productos terminados"),
                          Decimal("0"))
            exits = sum((m.cantidad for m in moves if m.tipo == "SALIDA"), Decimal("0"))
            adjustments = sum((self._movement_effect(m) for m in moves if m.tipo == "AJUSTE"), Decimal("0"))
            expected_stock = initial + entries - exits + adjustments
            if expected_stock == product.stock_actual:
                continue
            inconsistencies += 1
            last_move = max(moves, key=lambda m: (m.fecha, m.pk)) if moves else None
            previous = expected_stock - self._movement_effect(last_move) if last_move else Decimal("0")
            self.stdout.write(
                "\nINCONSISTENCIA DE RECONSTRUCCIÓN DE STOCK\n"
                f"Producto: {product.codigo} — {product.nombre}\n"
                f"Unidad de medida: {product.unidad_medida.codigo} ({product.unidad_medida.simbolo})\n"
                f"Movimiento ID: {last_move.pk if last_move else 'N/A'}\n"
                f"Tipo: {last_move.tipo if last_move else 'N/A'}\n"
                f"Documento origen: {last_move.descripcion if last_move else 'N/A'}\n"
                f"Cantidad almacenada: {last_move.cantidad if last_move else Decimal('0')}\n"
                f"Cantidad esperada: {last_move.cantidad if last_move else Decimal('0')}\n"
                f"Stock anterior: {previous}\nStock posterior: {expected_stock}\n"
                f"Diferencia: {product.stock_actual - expected_stock}\n"
                f"Fecha: {last_move.fecha if last_move else 'N/A'}\n"
                f"Stock inicial: {initial}\nTotal entradas: {entries}\nTotal salidas: {exits}\n"
                f"Ajustes válidos: {adjustments}\nStock esperado: {expected_stock}\n"
                f"Stock almacenado: {product.stock_actual}\n"
                f"Diferencia: {product.stock_actual - expected_stock}\n"
            )
        return inconsistencies

    def _validate(self, seed):
        bad_sales = sum(1 for x in Venta.objects.prefetch_related("detalles")
            if not x.detalles.exists() or x.subtotal != sum((d.subtotal for d in x.detalles.all()), Decimal(0))
            or x.total != x.subtotal + x.impuesto - x.descuento)
        bad_purchases = sum(1 for x in Compra.objects.prefetch_related("detalles")
            if not x.detalles.exists() or x.subtotal != sum((d.subtotal for d in x.detalles.all()), Decimal(0))
            or x.total != x.subtotal + x.impuesto)
        bad_cxc = sum(1 for x in CuentaPorCobrar.objects.prefetch_related("pagos") if x.saldo < 0 or
            x.saldo != x.monto_original - sum((p.monto for p in x.pagos.filter(estado="APLICADO")), Decimal(0)))
        bad_cxp = sum(1 for x in CuentaPorPagar.objects.prefetch_related("pagos") if x.saldo < 0 or
            x.saldo != x.monto_original - sum((p.monto for p in x.pagos.filter(estado="APLICADO")), Decimal(0)))
        negative = Producto.objects.filter(stock_actual__lt=0).count()
        inconsistent_moves = self._inventory_diagnostics()
        products_kg = Producto.objects.filter(unidad_medida__codigo="KG").count()
        products_unit = Producto.objects.filter(unidad_medida__codigo="UND").count()
        weight_sales = DetalleVenta.objects.filter(producto__unidad_medida__codigo="KG").count()
        amount_sales = Venta.objects.filter(observaciones__icontains="monto solicitado").count()
        generic_sales = Venta.objects.filter(cliente__nombre="Estimado Cliente").count()
        generic_credit_sales = Venta.objects.filter(
            cliente__nombre="Estimado Cliente", tipo_venta="CREDITO").count()
        generic_percentage = Decimal(generic_sales * 100) / Decimal(Venta.objects.count())
        forbidden_prefixes = (
            Venta.objects.filter(numero_comprobante__istartswith="DEMO-").count()
            + Compra.objects.filter(numero_factura__istartswith="DEMO-").count()
            + PagoCliente.objects.filter(referencia__istartswith="DEMO-").count()
            + PagoProveedor.objects.filter(referencia__istartswith="DEMO-").count()
            + Cliente.objects.filter(identificacion__istartswith="DEMO-").count()
            + Proveedor.objects.filter(identificacion__istartswith="DEMO-").count()
        )
        implausible_supplier_emails = Proveedor.objects.filter(
            Q(correo__isnull=True) | Q(correo="") | Q(correo__icontains="example")
        ).count()
        orphan = Venta.objects.filter(detalles__isnull=True).count() + Compra.objects.filter(detalles__isnull=True).count()
        debit = DetalleAsiento.objects.filter(asiento__estado="CONTABILIZADO").aggregate(v=Sum("debe"))["v"] or Decimal(0)
        credit = DetalleAsiento.objects.filter(asiento__estado="CONTABILIZADO").aggregate(v=Sum("haber"))["v"] or Decimal(0)
        errors = []
        for count, label in ((bad_sales, "ventas"), (bad_purchases, "compras"), (bad_cxc, "CxC"),
                             (bad_cxp, "CxP"), (negative, "inventario negativo"),
                             (inconsistent_moves, "movimientos inconsistentes"), (orphan, "relaciones huérfanas")):
            if count: errors.append(f"{count} {label}")
        if abs(debit - credit) > CENT: errors.append("contabilidad desbalanceada")
        if Venta.objects.filter(total__gt=2000000).exists(): errors.append("venta superior a ₡2.000.000")
        if not Decimal("90") <= generic_percentage <= Decimal("95"):
            errors.append("proporción de ventas a Estimado Cliente fuera de 90–95%")
        if generic_credit_sales: errors.append("venta a crédito asociada a Estimado Cliente")
        if forbidden_prefixes: errors.append("código o identificador con prefijo DEMO-")
        if implausible_supplier_emails: errors.append("correo de proveedor no plausible")
        if errors: raise CommandError("Validación demo fallida: " + "; ".join(errors))
        return dict(seed=seed, users=User.objects.filter(username=os.getenv("DEMO_USERNAME", "demo")).count(),
            customers=Cliente.objects.count(), suppliers=Proveedor.objects.count(), products=Producto.objects.count(),
            sales=Venta.objects.count(), cash_sales=Venta.objects.filter(tipo_venta="CONTADO").count(),
            credit_sales=Venta.objects.filter(tipo_venta="CREDITO").count(), purchases=Compra.objects.count(),
            cash_purchases=Compra.objects.filter(tipo_compra="CONTADO").count(),
            credit_purchases=Compra.objects.filter(tipo_compra="CREDITO").count(),
            generic_sales=generic_sales, generic_percentage=generic_percentage,
            forbidden_prefixes=forbidden_prefixes,
            supplier_payments=PagoProveedor.objects.count(), customer_payments=PagoCliente.objects.count(),
            sales_total=Venta.objects.aggregate(v=Sum("total"))["v"] or 0,
            purchases_total=Compra.objects.aggregate(v=Sum("total"))["v"] or 0,
            negative=negative, bad_sales=bad_sales, bad_purchases=bad_purchases,
            bad_cxc=bad_cxc, bad_cxp=bad_cxp, orphan=orphan, debit=debit, credit=credit,
            inconsistent_moves=inconsistent_moves, products_kg=products_kg,
            products_unit=products_unit, weight_sales=weight_sales, amount_sales=amount_sales,
            generic_credit_sales=generic_credit_sales)

    def _summary(self, m):
        line = "=" * 56
        self.stdout.write(f"\n{line}\n BYTEFORGE TECHNOLOGIES — DEMO DATA\n{line}\nPeriodo: {START} → {END}\nSeed: {m['seed']}\n")
        fields = [("Usuarios principales", "users"), ("Clientes", "customers"), ("Proveedores", "suppliers"),
            ("Productos", "products"), ("Ventas", "sales"), ("Ventas contado", "cash_sales"),
            ("Ventas crédito", "credit_sales"), ("Ventas Estimado Cliente", "generic_sales"),
            ("Compras", "purchases"), ("Compras contado", "cash_purchases"),
            ("Compras crédito", "credit_purchases"), ("Pagos CxP", "supplier_payments"), ("Abonos CxC", "customer_payments")]
        for label, key in fields: self.stdout.write(f"{label:.<38} {m[key]:>6}")
        self.stdout.write(f"Porcentaje Estimado Cliente{'.' * 12} {m['generic_percentage']:>5.2f}%")
        self.stdout.write(f"Ventas crédito genéricas{'.' * 12} {m['generic_credit_sales']:>6}")
        for label, key in [("Productos por kg", "products_kg"), ("Productos por unidad", "products_unit"),
                           ("Ventas por peso", "weight_sales"), ("Ventas simuladas por monto", "amount_sales")]:
            self.stdout.write(f"{label:.<38} {m[key]:>6}")
        self.stdout.write(f"Total ventas{'.' * 25} ₡{m['sales_total']:>12,.2f}\nTotal compras{'.' * 24} ₡{m['purchases_total']:>12,.2f}\n")
        for label, key in [("Stock negativo", "negative"), ("Ventas inconsistentes", "bad_sales"),
            ("Compras inconsistentes", "bad_purchases"), ("CxC inconsistentes", "bad_cxc"),
            ("CxP inconsistentes", "bad_cxp"), ("Prefijos DEMO-", "forbidden_prefixes"),
            ("Movimientos inconsistentes", "inconsistent_moves"),
            ("Relaciones huérfanas", "orphan")]:
            self.stdout.write(f"{label:.<38} {m[key]:>6}")
        self.stdout.write(f"Débitos{'.' * 31} ₡{m['debit']:>12,.2f}\nCréditos{'.' * 30} ₡{m['credit']:>12,.2f}\nDiferencia{'.' * 28} ₡{abs(m['debit'] - m['credit']):>12,.2f}")
        for period in PeriodoContable.objects.order_by("fecha_inicio"):
            self.stdout.write(f"{period.nombre:.<38} {'CERRADO' if period.cerrado else 'ABIERTO':>10}")
        self.stdout.write(self.style.SUCCESS(f"\n{line}\n DEMO DATABASE VALIDATED\n{line}"))
