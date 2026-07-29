from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0003_alter_detalleventa_options_alter_venta_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="SecuenciaComprobanteVenta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("periodo", models.CharField(max_length=8, unique=True)),
                ("ultimo_numero", models.PositiveBigIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Secuencia de comprobante de venta",
                "verbose_name_plural": "Secuencias de comprobantes de venta",
            },
        ),
    ]
