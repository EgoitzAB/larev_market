from django.db import models
from django.contrib.auth.models import User

class Direccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones')
    nombre_completo = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    pais = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    es_direccion_envio = models.BooleanField(default=True)  # Diferenciar entre envío y facturación

    def __str__(self):
        return f"{self.nombre_completo} - {self.direccion}, {self.ciudad} ({self.pais})"
