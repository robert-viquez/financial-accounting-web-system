from django.db import migrations


def crear_cliente_generico(apps, schema_editor):
    Cliente = apps.get_model("terceros", "Cliente")
    Cliente.objects.get_or_create(
        nombre="Estimado Cliente",
        defaults={"estado": True, "dias_credito": 30},
    )


def eliminar_cliente_generico(apps, schema_editor):
    Cliente = apps.get_model("terceros", "Cliente")
    Cliente.objects.filter(
        nombre="Estimado Cliente",
        identificacion__isnull=True,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("terceros", "0002_cliente_dias_credito_proveedor_dias_credito"),
    ]

    operations = [
        migrations.RunPython(crear_cliente_generico, eliminar_cliente_generico),
    ]
