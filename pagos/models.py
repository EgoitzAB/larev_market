from django.db import models
from django.conf import settings
from tienda.models import ProductoVariante
from checkout.models import Direccion
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from coupon.models import Coupon


class Orden(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('fallida', 'Fallida'),
        ('cancelada', 'Cancelada'),
    )

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, related_name="ordenes_envio")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    stock_reservado = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon,
                               related_name='ordenes',
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL)
    
    descuento = models.IntegerField(default=0,
                                    validators=[MinValueValidator(0),
                                                MaxValueValidator(100)])

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente.username}"
    
    def get_total_cost_before_discount(self):
        """
        Método para obtener el costo total de la orden antes de aplicar el descuento.
        """
        return sum(item.precio_unitario * item.cantidad for item in self.items.all())
    
    def get_discount(self):
        total_cost = self.get_total_cost_before_discount()
        if self.coupon and hasattr(self.coupon, 'discount'):
            return (total_cost * self.coupon.discount) / 100
        return Decimal(0)
    
    
    def get_total_cost(self):
        """
        Método para obtener el costo total de la orden después de aplicar el descuento.
        """
        total_cost = self.get_total_cost_before_discount()
        discount = self.get_discount()
        return total_cost - discount

    @classmethod
    def crear_orden(cls, cliente, direccion_envio, carrito, coupon=None):
        """
        Crea una orden con sus items, aplicando un cupón si existe.
        """
        total = carrito.get_total_price_after_discount()  # Aplicar descuento
        descuento = carrito.get_discount()  # Obtener el monto del descuento

        # Crear la orden
        orden = cls.objects.create(
            cliente=cliente,
            direccion_envio=direccion_envio,
            total=total,
            estado='pendiente',
            coupon=coupon,  # Asignar el cupón a la orden
            descuento=descuento,  # Guardar el descuento aplicado
        )

        # Agregar los items de la orden
        for item in carrito:
            ItemOrden.objects.create(
                orden=orden,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
            )

        return orden


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
