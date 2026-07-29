from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("usuarios", "0004_asignar_administradores")]

    operations = [
        migrations.AddField(
            model_name="configuracionempresa",
            name="lector_codigo_barras",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="configuracionempresa",
            name="prefijo_productos",
            field=models.CharField(blank=True, default="", max_length=8),
        ),
    ]
