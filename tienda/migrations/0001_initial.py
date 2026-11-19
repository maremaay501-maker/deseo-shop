import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

CATEGORIAS = [
    ("lenceria", "Lencería"),
    ("babydoll", "Babydolls"),
    ("conjuntos", "Conjuntos"),
    ("para_el", "Para él"),
    ("divertidos", "Divertidos"),
]


def usuario():
    return models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)


def id_():
    return models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Producto",
            fields=[
                ("id", id_()),
                ("nombre", models.CharField(max_length=120)),
                ("categoria", models.CharField(choices=CATEGORIAS, default="lenceria", max_length=20)),
                ("descripcion", models.CharField(blank=True, help_text="Frase corta (como en la tarjeta)", max_length=160)),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                ("precio_anterior", models.DecimalField(blank=True, decimal_places=2, help_text="Opcional: precio tachado", max_digits=10, null=True)),
                ("stock", models.PositiveIntegerField(default=0)),
                ("imagen", models.FileField(blank=True, upload_to="productos/")),
                ("destacado", models.BooleanField(default=False, help_text="Aparece en la sección rosa «Nuevo»")),
                ("creado", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-creado"]},
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                ("id", id_()),
                ("titulo", models.CharField(max_length=120)),
                ("url", models.URLField(blank=True, help_text="Enlace de YouTube")),
                ("archivo", models.FileField(blank=True, upload_to="videos/")),
                ("creado", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-creado"]},
        ),
        migrations.CreateModel(
            name="Foto",
            fields=[
                ("id", id_()),
                ("imagen", models.FileField(upload_to="fotos/")),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("usuario", usuario()),
            ],
            options={"ordering": ["-fecha"]},
        ),
        migrations.CreateModel(
            name="Mensaje",
            fields=[
                ("id", id_()),
                ("texto", models.CharField(max_length=300)),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("usuario", usuario()),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="RespuestaEncuesta",
            fields=[
                ("id", id_()),
                ("satisfaccion", models.PositiveSmallIntegerField()),
                ("categoria_favorita", models.CharField(choices=CATEGORIAS, max_length=20)),
                ("recomendaria", models.BooleanField(default=True)),
                ("comentario", models.TextField(blank=True)),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("usuario", usuario()),
            ],
            options={"ordering": ["-fecha"]},
        ),
        migrations.CreateModel(
            name="Ubicacion",
            fields=[
                ("id", id_()),
                ("latitud", models.FloatField()),
                ("longitud", models.FloatField()),
                ("distancia_km", models.FloatField()),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("usuario", usuario()),
            ],
            options={"ordering": ["-fecha"]},
        ),
        migrations.CreateModel(
            name="Compra",
            fields=[
                ("id", id_()),
                ("cantidad", models.PositiveIntegerField(default=1)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("producto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tienda.producto")),
                ("usuario", usuario()),
            ],
            options={"ordering": ["-fecha"]},
        ),
    ]
