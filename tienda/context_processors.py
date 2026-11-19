from django.conf import settings


def marca(request):
    """Identidad y datos de la tienda disponibles en todas las plantillas."""
    return {
        "MARCA": settings.MARCA,
        "SLOGAN": settings.SLOGAN,
        "TIENDA_NOMBRE": settings.TIENDA_NOMBRE,
        "TIENDA_LAT": settings.TIENDA_LAT,
        "TIENDA_LNG": settings.TIENDA_LNG,
    }
