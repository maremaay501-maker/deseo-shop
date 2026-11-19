from django.contrib import admin

from .models import Compra, Foto, Mensaje, Producto, RespuestaEncuesta, Ubicacion, Video

for modelo in (Compra, Producto, Mensaje, Video, RespuestaEncuesta, Foto, Ubicacion):
    admin.site.register(modelo)
