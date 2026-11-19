from django.contrib.auth.views import LoginView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path(
        "login/",
        LoginView.as_view(
            template_name="tienda/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("salir/", views.salir, name="logout"),
    path("registro/", views.registro, name="registro"),
    path("panel/", views.panel, name="panel"),
    path("identidad/", views.identidad, name="identidad"),
    # catálogo + CRUD + compras
    path("catalogo/", views.catalogo, name="catalogo"),
    path("catalogo/nuevo/", views.producto_crear, name="producto_crear"),
    path("catalogo/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("catalogo/<int:pk>/comprar/", views.comprar, name="comprar"),
    path("catalogo/<int:pk>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
    path("mis-compras/", views.mis_compras, name="mis_compras"),
    # actividades
    path("mapa/", views.mapa, name="mapa"),
    path("api/ubicacion/", views.guardar_ubicacion, name="guardar_ubicacion"),
    path("chat/", views.chat, name="chat"),
    path("api/chat/", views.chat_mensajes, name="chat_mensajes"),
    path("api/chat/enviar/", views.chat_enviar, name="chat_enviar"),
    path("videos/", views.videos, name="videos"),
    path("videos/<int:pk>/eliminar/", views.video_eliminar, name="video_eliminar"),
    path("encuesta/", views.encuesta, name="encuesta"),
    path("camara/", views.camara, name="camara"),
    path("api/foto/", views.guardar_foto, name="guardar_foto"),
]
