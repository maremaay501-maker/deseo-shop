from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("tienda.urls")),
    # Archivos subidos (videos, fotos, imágenes de productos). Se sirven también
    # con DEBUG=False para que funcionen en Render (suficiente para un proyecto escolar).
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
