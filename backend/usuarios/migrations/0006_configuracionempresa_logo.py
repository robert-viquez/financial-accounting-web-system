from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("usuarios", "0005_configuracion_negocio")]

    operations = [
        migrations.AddField(
            model_name="configuracionempresa",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="empresa/logos/",
            ),
        ),
    ]
