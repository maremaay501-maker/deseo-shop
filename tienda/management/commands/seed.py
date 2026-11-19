from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tienda.models import Producto, Video

# nombre, categoría, frase corta, precio, precio anterior, stock, imagen (media/catalogo/), destacado
PRODUCTOS = [
    ("Vestido de satín", "lenceria", "satín negro + encaje marfil", 649, None, 10, "vestido_satin.jpg", False),
    ("Babydoll Medianoche", "babydoll", "encaje negro + panty a juego", 459, None, 12, "babydoll_medianoche.jpg", False),
    ("Babydoll Flores", "babydoll", "tul transparente + flores bordadas", 399, None, 15, "babydoll_flores.jpg", False),
    ("Babydoll Vino", "babydoll", "tul vino + ligueros + choker", 529, None, 8, "babydoll_vino.jpg", False),
    ("Conjunto Orquídea", "conjuntos", "bordado de orquídeas + choker de perlas", 789, 989, 6, "conjunto_orquidea.jpg", True),
    ("Tanga Elefante", "para_el", "negra, con ojitos (regalo divertido)", 199, None, 20, "tanga_elefante_negra.jpg", False),
    ("Tanga Elefante Roja", "para_el", "roja, para despedidas de soltero", 199, None, 18, "tanga_elefante_roja.jpg", False),
    ("Tanga Roja «Sapito»", "divertidos", "tanga roja clásica, foto de broma", 149, None, 25, "tanga_roja_sapito.jpg", False),
    ("Destapador artesanal", "divertidos", "madera pintada a mano, souvenir", 129, None, 30, "destapador_artesanal.jpg", False),
    ("Destapador arcoíris", "divertidos", "edición de colores, el más pedido", 149, None, 4, "destapador_arcoiris.jpg", False),
]


class Command(BaseCommand):
    help = "Crea usuarios de prueba (admin y cliente), productos y el video de la tienda."

    def handle(self, *args, **opciones):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@deseo.mx", "admin123", first_name="Administradora")
        if not User.objects.filter(username="cliente").exists():
            User.objects.create_user("cliente", "cliente@deseo.mx", "cliente123", first_name="Cliente")

        for nombre, cat, desc, precio, antes, stock, img, dest in PRODUCTOS:
            Producto.objects.get_or_create(
                nombre=nombre,
                defaults=dict(
                    categoria=cat, descripcion=desc, precio=precio, precio_anterior=antes,
                    stock=stock, imagen=f"catalogo/{img}", destacado=dest,
                ),
            )

        # Video de la tienda (el archivo está en media/videos/video_1.mp4)
        if not Video.objects.filter(archivo="videos/video_1.mp4").exists():
            Video.objects.create(titulo="Try-on: looks de la temporada", archivo="videos/video_1.mp4")

        self.stdout.write(self.style.SUCCESS("Listo. Admin: admin / admin123  |  Cliente: cliente / cliente123"))
