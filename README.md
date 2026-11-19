# Deseo — Sexy Shop (Django)

## Cómo correrlo

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (en Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed          # crea usuarios, los 10 productos con sus fotos y el video
python manage.py runserver
```

Abre http://127.0.0.1:8000/ (te manda al login).

| Rol     | Usuario   | Contraseña   | Entra a                    |
|---------|-----------|--------------|----------------------------|
| Admin   | `admin`   | `admin123`   | Panel de métricas          |
| Cliente | `cliente` | `cliente123` | Home de la tienda          |

Los clientes nuevos se registran en `/registro/`. El admin de Django queda en `/django-admin/`.

> La geolocalización y la cámara solo funcionan en `localhost` o con HTTPS.

## Qué cubre la rúbrica

| Punto de la rúbrica | Dónde está |
|---|---|
| Login antes de todo + 2 tipos de usuario | `login/`, decorador `solo_admin` y `inicio` en `tienda/views.py` |
| Home de admin con métricas | `panel/` → `templates/tienda/panel.html` (Chart.js) |
| Home de cliente (diseño de referencia: hero, menú con píldoras, 2 carruseles, sección rosa «Nuevo», video) | `templates/tienda/home_cliente.html` |
| Botón de comprar + «Mis compras» | `comprar` y `mis_compras` en `views.py`, icono de bolsa en el menú |
| Producto | Modelo `Producto` (lencería, babydolls, conjuntos, para él, divertidos) |
| Identidad: logo, paleta, slogan, tipografías | Página `identidad/`, `static/tienda/img/logo.svg`, variables en `css/estilo.css`, `MARCA` y `SLOGAN` en `settings.py` |
| Menú | `templates/tienda/base.html` (cambia según el rol) |
| Capturar ubicación + mapa/distancia | `mapa/` (Leaflet + OpenStreetMap, fórmula de Haversine) |
| CRUD | `catalogo/` (crear, editar, eliminar — solo admin) |
| Blog (chat) | `chat/` (se actualiza cada 3 s) |
| Videos | `videos/` (YouTube o archivo; el admin los agrega) |
| Encuesta | `encuesta/` (cliente) → resultados en el panel del admin |
| Tomar fotos | `camara/` (getUserMedia, se guardan en `media/fotos/`) |

## Personalizar

- **Ubicación de la tienda (UPVM, Tultitlán):** `TIENDA_LAT` y `TIENDA_LNG` al final de `deseo/settings.py`.
- **Nombre y slogan:** `MARCA`, `SLOGAN`, `TIENDA_NOMBRE` en el mismo archivo.
- **Colores:** variables `:root` al inicio de `tienda/static/tienda/css/estilo.css`.

## Identidad

- **Logotipo/imagotipo:** labios rosa y caramelo dentro de un círculo vino con aro punteado (`logo.svg`) + el nombre «Deseo».
- **Paleta:** vino `#4e0f1d`, vino claro `#7a1f2e`, caramelo `#b97a64`, rosa empolvado `#f6c6c6`, arena `#e9ddcf`, crema `#faf5ef`.
- **Tipografías:** Archivo Black (títulos), Pinyon Script (acentos tipo «Bienvenida»), Poppins (texto).
- **Slogan:** «Atrévete a desear.»
- Es un sitio +18: el registro pide confirmar mayoría de edad.

## Publicarlo (GitHub + Aiven + Render)

1. **GitHub:** sube esta carpeta a un repositorio (el `.gitignore` ya excluye `venv`, `db.sqlite3`, etc.).
2. **Aiven:** crea un servicio **PostgreSQL** (plan Free) y copia su **Service URI** (`postgres://avnadmin:...?sslmode=require`).
3. **Render:** New → Web Service → conecta el repo y configura:
   - Build Command: `bash build.sh`
   - Start Command: `gunicorn deseo.wsgi:application`
   - Environment: `DATABASE_URL` = Service URI de Aiven, `SECRET_KEY` = texto largo cualquiera, `DEBUG` = `False`
4. Abre el link `https://<tu-app>.onrender.com` y entra con `admin` / `admin123` o `cliente` / `cliente123`.

> En el plan gratis de Render, las fotos que se suban desde la página se borran cuando el servicio se reinicia. Los datos (usuarios, productos, compras, encuestas) quedan guardados en Aiven.
