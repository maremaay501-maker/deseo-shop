from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Producto, RespuestaEncuesta, Video


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"placeholder": "Usuario", "autofocus": True})
        self.fields["password"].widget.attrs.update({"placeholder": "Contraseña"})


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=60)
    email = forms.EmailField(label="Correo")
    mayor_edad = forms.BooleanField(
        label="Confirmo que soy mayor de 18 años",
        error_messages={"required": "Debes ser mayor de edad para registrarte."},
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre", "categoria", "descripcion", "precio", "precio_anterior",
            "stock", "imagen", "destacado",
        ]
        widgets = {"imagen": forms.ClearableFileInput(attrs={"accept": "image/*"})}


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["titulo", "url", "archivo"]
        widgets = {"archivo": forms.ClearableFileInput(attrs={"accept": "video/*"})}

    def clean(self):
        datos = super().clean()
        url, archivo = datos.get("url"), datos.get("archivo")
        if not url and not archivo:
            raise forms.ValidationError("Agrega un enlace de YouTube o sube un archivo.")
        if url and not Video(url=url).youtube_id:
            raise forms.ValidationError("No reconozco ese enlace de YouTube.")
        return datos


class EncuestaForm(forms.ModelForm):
    satisfaccion = forms.ChoiceField(
        label="¿Qué tan satisfecha/o estás con la tienda?",
        choices=[(i, f"{i}") for i in range(1, 6)],
        widget=forms.RadioSelect,
    )
    recomendaria = forms.TypedChoiceField(
        label="¿Nos recomendarías?",
        choices=[(True, "Sí"), (False, "No")],
        coerce=lambda v: v in (True, "True", "true", "1"),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = RespuestaEncuesta
        fields = ["satisfaccion", "categoria_favorita", "recomendaria", "comentario"]
        labels = {
            "categoria_favorita": "¿Qué colección te gusta más?",
            "comentario": "Comentarios",
        }
        widgets = {"comentario": forms.Textarea(attrs={"rows": 3})}
