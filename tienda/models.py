import re

from django.conf import settings
from django.db import models


class Producto(models.Model):
    CATEGORIAS = [
        ("lenceria", "Lencería"),
        ("babydoll", "Babydolls"),
        ("conjuntos", "Conjuntos"),
        ("para_el", "Para él"),
        ("divertidos", "Divertidos"),
    ]

    nombre = models.CharField(max_length=120)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="lenceria")
    descripcion = models.CharField(max_length=160, blank=True, help_text="Frase corta (como en la tarjeta)")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_anterior = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Opcional: precio tachado"
    )
    stock = models.PositiveIntegerField(default=0)
    imagen = models.FileField(upload_to="productos/", blank=True)
    destacado = models.BooleanField(default=False, help_text="Aparece en la sección rosa «Nuevo»")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return self.nombre

    @property
    def descuento(self):
        """Porcentaje de descuento si tiene precio anterior."""
        if self.precio_anterior and self.precio_anterior > self.precio:
            return round(100 - (self.precio * 100 / self.precio_anterior))
        return 0


class Mensaje(models.Model):
    """Mensajes del blog / chat."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.CharField(max_length=300)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.usuario}: {self.texto[:30]}"


class Video(models.Model):
    titulo = models.CharField(max_length=120)
    url = models.URLField(blank=True, help_text="Enlace de YouTube")
    archivo = models.FileField(upload_to="videos/", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return self.titulo

    @property
    def youtube_id(self):
        patron = r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})"
        m = re.search(patron, self.url or "")
        return m.group(1) if m else ""


class RespuestaEncuesta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    satisfaccion = models.PositiveSmallIntegerField()
    categoria_favorita = models.CharField(max_length=20, choices=Producto.CATEGORIAS)
    recomendaria = models.BooleanField(default=True)
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]


class Foto(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    imagen = models.FileField(upload_to="fotos/")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]


class Ubicacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    latitud = models.FloatField()
    longitud = models.FloatField()
    distancia_km = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]


class Compra(models.Model):
    """Compra sencilla: el cliente presiona «Comprar» y se descuenta 1 del stock."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.usuario} compró {self.producto}"
