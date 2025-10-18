from django.contrib import admin
from .models import Evento, RegistroEvento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "organizador", "fecha_inicio", "fecha_fin", "creado")
    list_filter = ("organizador",)
    search_fields = ("titulo", "descripcion")

@admin.register(RegistroEvento)
class RegistroEventoAdmin(admin.ModelAdmin):
    list_display = ("id", "evento", "usuario", "estado", "fecha_registro")
    list_filter = ("estado", "evento")
    search_fields = ("usuario__username", "evento__titulo")
