from django.db import migrations


def asignar_administradores(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    administradores, _ = Group.objects.get_or_create(name="Administrador")
    for usuario in User.objects.filter(is_staff=True):
        usuario.groups.add(administradores)


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0003_registroauditoria"),
    ]

    operations = [
        migrations.RunPython(asignar_administradores, migrations.RunPython.noop),
    ]
