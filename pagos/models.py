from django.db import models
from django.conf import settings
from tienda.models import ProductoVariante
from checkout.models import Direccion

class Orden(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completada', 'Completada'),
        ('fallida', 'Fallida'),
        ('cancelada', 'Cancelada'),
    )

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, related_name="ordenes_envio")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente.username}"


class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(ProductoVariante, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class Pago(models.Model):
    orden = models.OneToOneField(Orden, related_name='pago', on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=(
        ('pendiente', 'Pendiente'),
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
    ), default='pendiente')
    referencia = models.CharField(max_length=255, blank=True, null=True)
    fecha_pago = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Pago para Orden #{self.orden.id} - Estado: {self.estado}"
