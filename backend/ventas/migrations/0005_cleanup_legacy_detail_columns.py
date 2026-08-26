from django.db import migrations


def make_legacy_column_compatible(apps, schema_editor):
    """Keep prototype data but stop its obsolete NOT NULL column blocking inserts."""
    table = "ventas_detalleventa"
    with schema_editor.connection.cursor() as cursor:
        columns = {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(cursor, table)
        }
    if "cantidad_inventario" in columns and schema_editor.connection.vendor == "mysql":
        schema_editor.execute(
            "ALTER TABLE `ventas_detalleventa` "
            "ALTER COLUMN `cantidad_inventario` SET DEFAULT 0"
        )


class Migration(migrations.Migration):
    atomic = False
    dependencies = [("ventas", "0004_secuenciacomprobanteventa")]
    operations = [migrations.RunPython(make_legacy_column_compatible, migrations.RunPython.noop)]
