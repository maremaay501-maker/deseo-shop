import base64
import json
import uuid
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import EncuestaForm, ProductoForm, RegistroForm, VideoForm
from .models import Compra, Foto, Mensaje, Producto, RespuestaEncuesta, Ubicacion, Video


def solo_admin(vista):
    """Permite el acceso únicamente a usuarios administradores (is_staff)."""

    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Esa sección es solo para administradores.")
            return redirect("inicio")
        return vista(request, *args, **kwargs)

    return login_required(envoltura)


# ------------------------------------------------------------------ acceso
def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")
    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()  # los registros nuevos son clientes (is_staff=False)
        login(request, usuario)
        messages.success(request, "¡Cuenta creada! Bienvenido a la tienda.")
        return redirect("inicio")
    return render(request, "tienda/registro.html", {"form": form})


@require_POST
def salir(request):
    logout(request)
    return redirect("login")


@login_required
def inicio(request):
    """Redirige según el tipo de usuario: admin -> panel, cliente -> home."""
    if request.user.is_staff:
        return redirect("panel")
    productos = list(Producto.objects.order_by("id"))
    mitad = (len(productos) + 1) // 2
    contexto = {
        # Dos filas de carrusel, como las dos filas de cafés del diseño
        "fila1": productos[:mitad],
        "fila2": productos[mitad:],
        "categorias": Producto.CATEGORIAS,
        "nuevo": Producto.objects.filter(destacado=True).first(),
        "video": Video.objects.first(),
    }
    return render(request, "tienda/home_cliente.html", contexto)


@login_required
def mis_compras(request):
    compras = Compra.objects.filter(usuario=request.user).select_related("producto")
    total = compras.aggregate(t=Sum("total"))["t"] or 0
    return render(request, "tienda/mis_compras.html", {"compras": compras, "total": total})


@login_required
def identidad(request):
    """Manual de identidad: logotipo, paleta, slogan y tipografías."""
    return render(request, "tienda/identidad.html")


# ------------------------------------------------------------ panel admin
@solo_admin
def panel(request):
    productos = Producto.objects
    valor_inventario = productos.aggregate(
        v=Sum(
            ExpressionWrapper(
                F("precio") * F("stock"),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )
    )["v"] or 0

    por_categoria = {
        fila["categoria"]: fila["n"]
        for fila in productos.values("categoria").annotate(n=Count("id"))
    }
    etiquetas = [nombre for _, nombre in Producto.CATEGORIAS]
    valores = [por_categoria.get(clave, 0) for clave, _ in Producto.CATEGORIAS]

    satisf = {
        fila["satisfaccion"]: fila["n"]
        for fila in RespuestaEncuesta.objects.values("satisfaccion").annotate(n=Count("id"))
    }
    satisf_valores = [satisf.get(i, 0) for i in range(1, 6)]

    ubicaciones = Ubicacion.objects.select_related("usuario")
    contexto = {
        "total_productos": productos.count(),
        "stock_total": productos.aggregate(s=Sum("stock"))["s"] or 0,
        "valor_inventario": valor_inventario,
        "total_clientes": User.objects.filter(is_staff=False).count(),
        "total_mensajes": Mensaje.objects.count(),
        "total_fotos": Foto.objects.count(),
        "total_encuestas": RespuestaEncuesta.objects.count(),
        "total_compras": Compra.objects.count(),
        "total_vendido": Compra.objects.aggregate(t=Sum("total"))["t"] or 0,
        "promedio_satisfaccion": RespuestaEncuesta.objects.aggregate(p=Avg("satisfaccion"))["p"],
        "distancia_promedio": ubicaciones.aggregate(d=Avg("distancia_km"))["d"],
        "bajo_stock": productos.filter(stock__lte=5).order_by("stock")[:6],
        "ultimas_ubicaciones": ubicaciones[:6],
        "mas_vendidos": Compra.objects.values("producto__nombre")
        .annotate(n=Sum("cantidad"), t=Sum("total"))
        .order_by("-n")[:6],
        "ultimas_compras": Compra.objects.select_related("usuario", "producto")[:6],
        "datos_categorias": {"labels": etiquetas, "values": valores},
        "datos_satisfaccion": {"labels": ["1", "2", "3", "4", "5"], "values": satisf_valores},
    }
    return render(request, "tienda/panel.html", contexto)


# ------------------------------------------------------- catálogo y CRUD
@login_required
def catalogo(request):
    productos = Producto.objects.all()
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "")
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if cat:
        productos = productos.filter(categoria=cat)
    return render(
        request,
        "tienda/catalogo.html",
        {"productos": productos, "q": q, "cat": cat, "categorias": Producto.CATEGORIAS},
    )


@login_required
@require_POST
def comprar(request, pk):
    """Botón de comprar: registra la compra de 1 producto y descuenta el stock."""
    with transaction.atomic():
        producto = get_object_or_404(Producto.objects.select_for_update(), pk=pk)
        if producto.stock < 1:
            messages.error(request, f"Lo sentimos, {producto.nombre} está agotado.")
        else:
            producto.stock -= 1
            producto.save(update_fields=["stock"])
            Compra.objects.create(
                usuario=request.user, producto=producto, cantidad=1, total=producto.precio
            )
            messages.success(request, f"¡Compraste {producto.nombre} por ${producto.precio}! Gracias por tu compra.")
    siguiente = request.POST.get("siguiente", "")
    if not url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        siguiente = "catalogo"
    return redirect(siguiente)


@solo_admin
def producto_crear(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto creado.")
        return redirect("catalogo")
    return render(request, "tienda/producto_form.html", {"form": form, "titulo": "Nuevo producto"})


@solo_admin
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("catalogo")
    return render(request, "tienda/producto_form.html", {"form": form, "titulo": "Editar producto"})


@solo_admin
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("catalogo")
    return render(request, "tienda/producto_borrar.html", {"producto": producto})


# ------------------------------------------------------------------- mapa
@login_required
def mapa(request):
    ultima = Ubicacion.objects.filter(usuario=request.user).first()
    return render(request, "tienda/mapa.html", {"ultima": ultima})


@login_required
@require_POST
def guardar_ubicacion(request):
    try:
        datos = json.loads(request.body)
        lat, lng = float(datos["lat"]), float(datos["lng"])
        distancia = float(datos["distancia_km"])
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos"}, status=400)
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return JsonResponse({"ok": False, "error": "Coordenadas fuera de rango"}, status=400)
    Ubicacion.objects.create(
        usuario=request.user, latitud=lat, longitud=lng, distancia_km=round(distancia, 2)
    )
    return JsonResponse({"ok": True})


# ------------------------------------------------------------ blog / chat
@login_required
def chat(request):
    return render(request, "tienda/chat.html")


@login_required
def chat_mensajes(request):
    try:
        despues = int(request.GET.get("despues", 0))
    except ValueError:
        despues = 0
    qs = Mensaje.objects.select_related("usuario").filter(id__gt=despues).order_by("-id")[:50]
    datos = [
        {
            "id": m.id,
            "usuario": m.usuario.first_name or m.usuario.username,
            "admin": m.usuario.is_staff,
            "propio": m.usuario_id == request.user.id,
            "texto": m.texto,
            "hora": m.fecha.astimezone().strftime("%d/%m %H:%M"),
        }
        for m in reversed(list(qs))
    ]
    return JsonResponse({"mensajes": datos})


@login_required
@require_POST
def chat_enviar(request):
    texto = request.POST.get("texto", "").strip()[:300]
    if not texto:
        return JsonResponse({"ok": False}, status=400)
    Mensaje.objects.create(usuario=request.user, texto=texto)
    return JsonResponse({"ok": True})


# ----------------------------------------------------------------- videos
@login_required
def videos(request):
    form = None
    if request.user.is_staff:
        form = VideoForm(request.POST or None, request.FILES or None)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Video agregado.")
            return redirect("videos")
    return render(request, "tienda/videos.html", {"videos": Video.objects.all(), "form": form})


@solo_admin
@require_POST
def video_eliminar(request, pk):
    get_object_or_404(Video, pk=pk).delete()
    messages.success(request, "Video eliminado.")
    return redirect("videos")


# --------------------------------------------------------------- encuesta
@login_required
def encuesta(request):
    form = EncuestaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        respuesta = form.save(commit=False)
        respuesta.usuario = request.user
        respuesta.save()
        messages.success(request, "¡Gracias por contestar la encuesta!")
        return redirect("inicio")
    return render(request, "tienda/encuesta.html", {"form": form})


# ----------------------------------------------------------------- cámara
@login_required
def camara(request):
    fotos = Foto.objects.select_related("usuario")
    if not request.user.is_staff:
        fotos = fotos.filter(usuario=request.user)
    return render(request, "tienda/camara.html", {"fotos": fotos[:12]})


@login_required
@require_POST
def guardar_foto(request):
    try:
        imagen = json.loads(request.body)["imagen"]
        _, b64 = imagen.split(",", 1)
        binario = base64.b64decode(b64)
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"ok": False, "error": "Imagen inválida"}, status=400)
    if len(binario) > 5 * 1024 * 1024:
        return JsonResponse({"ok": False, "error": "La foto pesa más de 5 MB"}, status=400)
    foto = Foto(usuario=request.user)
    foto.imagen.save(f"{request.user.username}_{uuid.uuid4().hex[:8]}.jpg", ContentFile(binario))
    return JsonResponse({"ok": True})
