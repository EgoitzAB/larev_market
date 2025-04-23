from django.db import models
from django.contrib.auth.models import User

class Direccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones', blank=True, null=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    provincia = models.CharField(max_length=100)

    PAIS_CHOICES = [('ES', 'España')]
    pais = models.CharField(max_length=2, choices=PAIS_CHOICES, default='ES')

    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=20)

    es_direccion_envio = models.BooleanField(default=True)
    es_direccion_tienda = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - {self.direccion}, {self.ciudad} (España)"
