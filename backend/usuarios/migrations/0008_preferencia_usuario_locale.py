from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0007_roles_negocio")]

    operations = [
        migrations.AddField(
            model_name="configuracionempresa",
            name="locale_predeterminado",
            field=models.CharField(
                choices=[("auto", "Automático"), ("es", "Español"), ("en", "English")],
                default="auto",
                max_length=4,
            ),
        ),
        migrations.CreateModel(
            name="PreferenciaUsuario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("locale", models.CharField(blank=True, choices=[("es", "Español"), ("en", "English")], default="", max_length=2)),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="preferencias", to="auth.user")),
            ],
            options={"verbose_name": "Preferencia de usuario"},
        ),
    ]
