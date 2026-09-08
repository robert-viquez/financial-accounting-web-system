from django.db import migrations, models


def crear_tipos_base(apps, schema_editor):
    TipoVenta = apps.get_model("ventas", "TipoVenta")
    TipoVenta.objects.get_or_create(codigo="CONTADO", defaults={"nombre": "Contado", "genera_credito": False})
    TipoVenta.objects.get_or_create(codigo="CREDITO", defaults={"nombre": "Crédito", "genera_credito": True})


class Migration(migrations.Migration):
    dependencies = [("ventas", "0007_comprobanteelectronico")]

    operations = [
        migrations.CreateModel(
            name="TipoVenta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=20, unique=True)),
                ("nombre", models.CharField(max_length=50, unique=True)),
                ("estado", models.BooleanField(default=True)),
                ("genera_credito", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Tipo de venta",
                "verbose_name_plural": "Tipos de venta",
                "ordering": ["nombre"],
            },
        ),
        migrations.RunPython(crear_tipos_base, migrations.RunPython.noop),
    ]
