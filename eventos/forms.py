from django import forms
from .models import Evento, RegistroEvento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ["titulo", "descripcion", "fecha_inicio", "fecha_fin"]

class RegistroEventoForm(forms.ModelForm):
    class Meta:
        model = RegistroEvento
        fields = []  # no pedimos campos; se toma usuario/evento del contexto
