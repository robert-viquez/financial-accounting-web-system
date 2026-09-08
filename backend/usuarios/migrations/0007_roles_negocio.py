from django.db import migrations


def configurar_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    permisos_por_rol = {
        "Ventas": ["ventas", "terceros"],
        "Inventario": ["inventario"],
        "Contabilidad": ["contabilidad", "finanzas"],
        "Gerencia": ["ventas", "compras", "inventario", "contabilidad", "finanzas"],
        "Operaciones": ["ventas", "compras", "inventario", "terceros", "finanzas"],
    }
    for nombre, aplicaciones in permisos_por_rol.items():
        rol, _ = Group.objects.get_or_create(name=nombre)
        rol.permissions.add(
            *Permission.objects.filter(content_type__app_label__in=aplicaciones)
        )


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0006_configuracionempresa_logo"),
    ]

    operations = [
        migrations.RunPython(configurar_roles, migrations.RunPython.noop),
    ]
