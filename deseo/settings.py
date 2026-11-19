import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# En tu compu funciona igual que antes. En Render estos valores salen de las
# variables de entorno (Environment) que configuras en el panel.
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-cambia-esto-antes-de-publicar")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]

# Render da el dominio (ej. deseo.onrender.com) en RENDER_EXTERNAL_HOSTNAME
CSRF_TRUSTED_ORIGINS = []
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    CSRF_TRUSTED_ORIGINS.append("https://" + os.environ["RENDER_EXTERNAL_HOSTNAME"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tienda",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # sirve CSS/imagenes en Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "deseo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tienda.context_processors.marca",
            ],
        },
    },
]

WSGI_APPLICATION = "deseo.wsgi.application"

# Sin DATABASE_URL usa SQLite (tu compu). En Render, DATABASE_URL es la
# "Service URI" de PostgreSQL de Aiven (postgres://...?sslmode=require).
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = []  # sin restricciones, es un proyecto escolar

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Los mapas de OpenStreetMap exigen que el navegador mande el Referer.
# Django por defecto usa "same-origin" (no lo manda) y OSM responde 403 "Access blocked".
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "login"

# ---- Identidad y ubicación de la tienda ----
# Tienda virtual: el punto de entrega de referencia es la UPVM
# (Av. Mexiquense s/n esq. Universidad Politécnica, Col. Villa Esmeralda, Tultitlán, Edo. Méx.)
MARCA = "Deseo"
SLOGAN = "Atrévete a desear."
TIENDA_NOMBRE = "Deseo Sexy Shop"
TIENDA_LAT = 19.642466   # latitud (UPVM)
TIENDA_LNG = -99.127836  # longitud (UPVM)
