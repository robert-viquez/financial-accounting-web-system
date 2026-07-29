from django.db import migrations, models
import django.db.models.deletion


def preparar_datos(apps, schema_editor):
    Categoria = apps.get_model("inventario", "CategoriaProducto")
    Unidad = apps.get_model("inventario", "UnidadMedida")
    unidades = {
        "KG": Unidad.objects.create(codigo="KG", nombre="Kilogramo", simbolo="kg"),
        "UND": Unidad.objects.create(
            codigo="UND", nombre="Unidad", simbolo="unidad", permite_decimales=False
        ),
        "PAQ": Unidad.objects.create(
            codigo="PAQ", nombre="Paquete", simbolo="paq.", permite_decimales=False
        ),
        "G": Unidad.objects.create(codigo="G", nombre="Gramo", simbolo="g"),
    }
    usados = set()
    for categoria in Categoria.objects.order_by("id"):
        palabras = [p for p in categoria.nombre.upper().split() if p]
        base = "".join(p[0] for p in palabras)[:6] or "CAT"
        codigo = base
        numero = 2
        while codigo in usados:
            codigo = f"{base[:8]}{numero}"
            numero += 1
        categoria.codigo = codigo
        categoria.save(update_fields=["codigo"])
        usados.add(codigo)

    Producto = apps.get_model("inventario", "Producto")
    for producto in Producto.objects.all():
        codigo_unidad = producto.unidad_medida_anterior or "KG"
        producto.unidad_medida = unidades.get(codigo_unidad, unidades["KG"])
        producto.codigo_barras = producto.codigo
        producto.save(update_fields=["unidad_medida", "codigo_barras"])


class Migration(migrations.Migration):

    dependencies = [("inventario", "0002_movimientoinventario_usuario")]

    operations = [
        migrations.CreateModel(
            name="UnidadMedida",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=10, unique=True)),
                ("nombre", models.CharField(max_length=60, unique=True)),
                ("simbolo", models.CharField(max_length=12)),
                ("permite_decimales", models.BooleanField(default=True)),
                ("estado", models.BooleanField(default=True)),
            ],
            options={"ordering": ["nombre"], "verbose_name": "Unidad de medida", "verbose_name_plural": "Unidades de medida"},
        ),
        migrations.AddField(
            model_name="categoriaproducto",
            name="codigo",
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AddField(
            model_name="producto",
            name="codigo_barras",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.RenameField(
            model_name="producto",
            old_name="unidad_medida",
            new_name="unidad_medida_anterior",
        ),
        migrations.AddField(
            model_name="producto",
            name="unidad_medida",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="productos", to="inventario.unidadmedida"),
        ),
        migrations.RunPython(preparar_datos, migrations.RunPython.noop),
        migrations.RemoveField(model_name="producto", name="unidad_medida_anterior"),
        migrations.AlterField(
            model_name="categoriaproducto",
            name="codigo",
            field=models.CharField(editable=False, max_length=12, unique=True),
        ),
    ]
