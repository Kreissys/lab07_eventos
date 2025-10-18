from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_organizados')
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha_inicio"]

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio:%Y-%m-%d %H:%M})"

    @property
    def inscritos(self):
        return self.registros.count()

class RegistroEvento(models.Model):
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (CONFIRMADO, "Confirmado"),
        (CANCELADO, "Cancelado"),
    ]

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='registros')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registros_evento')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)

    class Meta:
        unique_together = ("evento", "usuario")
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.usuario.username} -> {self.evento.titulo} [{self.estado}]"
