from django.db import migrations, models


def crear_lock(apps, schema_editor):
    apps.get_model("usuarios", "ConfiguracionInicialLock").objects.get_or_create(pk=1)


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0008_preferencia_usuario_locale")]

    operations = [
        migrations.CreateModel(
            name="ConfiguracionInicialLock",
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
            ],
        ),
        migrations.RunPython(crear_lock, migrations.RunPython.noop),
    ]
