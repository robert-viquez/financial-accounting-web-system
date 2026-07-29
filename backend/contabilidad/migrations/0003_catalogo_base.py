from django.db import migrations


def crear_catalogo(apps, schema_editor):
    Cuenta = apps.get_model("contabilidad", "CuentaContable")
    cuentas = {
        "1101": ("Caja y bancos", "ACTIVO", "DEUDORA"),
        "1102": ("Cuentas por cobrar", "ACTIVO", "DEUDORA"),
        "1201": ("Inventario", "ACTIVO", "DEUDORA"),
        "2101": ("Cuentas por pagar", "PASIVO", "ACREEDORA"),
        "3101": ("Patrimonio", "PATRIMONIO", "ACREEDORA"),
        "4101": ("Ventas", "INGRESO", "ACREEDORA"),
        "5101": ("Costo de ventas", "COSTO", "DEUDORA"),
    }
    for codigo, (nombre, tipo, naturaleza) in cuentas.items():
        Cuenta.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nombre": nombre,
                "tipo": tipo,
                "naturaleza": naturaleza,
                "permite_movimientos": True,
                "estado": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("contabilidad", "0002_asientocontable_detalleasiento_periodocontable_and_more"),
    ]

    operations = [
        migrations.RunPython(crear_catalogo, migrations.RunPython.noop),
    ]
