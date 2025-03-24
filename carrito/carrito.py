from decimal import Decimal
from django.conf import settings
from coupon.models import Coupon
from tienda.models import Producto, ProductoVariante
from django.contrib import messages

class Carrito:
    def __init__(self, request):
        """
        Inicializar el carrito.
        """
        self.session = request.session
        carrito = self.session.get(settings.CARRITO_SESSION_ID)
        if not carrito:
            carrito = self.session[settings.CARRITO_SESSION_ID] = {}
        self.carrito = carrito
        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self):
        """
        Iterar sobre los productos y recuperarlos de la base de datos.
        """
        product_ids = self.carrito.keys()
        productos = ProductoVariante.objects.filter(id__in=product_ids)
        carrito = self.carrito.copy()
        for producto in productos:
            carrito[str(producto.id)]['producto'] = producto
            carrito[str(producto.id)]['stock'] = producto.stock  # Agregar stock de la variante
        for item in carrito.values():
            item['precio'] = Decimal(item['precio'])
            item['precio_total'] = item['precio'] * item['cantidad']
            yield item
    

    def __bool__(self):
        """
        Devuelve True si el carrito no está vacío.
        """
        return bool(self.carrito)

    def __len__(self):
        """
        Contar los items del carrito.
        """
        return sum(item['cantidad'] for item in self.carrito.values())

    def añadir(self, producto, cantidad=1, sobreescribir=False):
        """
        Añade un producto o actualiza su cantidad. Ajusta según disponibilidad.
        """
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {'cantidad': 0, 'precio': str(producto.precio)}

        if sobreescribir:
            nueva_cantidad = cantidad
        else:
            nueva_cantidad = self.carrito[producto_id]['cantidad'] + cantidad

        # Chequear disponibilidad de stock
        if nueva_cantidad > producto.stock:
            nueva_cantidad = producto.stock  # Ajustar al máximo disponible

        self.carrito[producto_id]['cantidad'] = nueva_cantidad
        self.save()

    def eliminar(self, producto):
        """
        Eliminar un producto del carrito.
        """
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.save()

    def limpiar(self):
        """
        Eliminar el carrito de la sesión.
        """
        del self.session[settings.CARRITO_SESSION_ID]
        self.save()

    def carrito_total(self):
        """
        Calcular el total del carrito.
        """
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.carrito.values())

    def save(self):
        """
        Marcar la sesión como modificada para asegurar que los cambios se guarden.
        """
        self.session.modified = True

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                self.session['coupon_id'] = None
                messages.error("El cupón no es válido o ha expirado.")
        return None
    
    def apply_coupon(self, coupon_id):
        self.session['coupon_id'] = coupon_id
        self.save()

    def remove_coupon(self):
        self.session['coupon_id'] = None
        self.save()

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) \
                * self.carrito_total()
        return Decimal(0)

    def get_total_price_after_discount(self):
        """ Obtiene el total del carrito después del descuento, asegurando que no sea negativo. """
        total_con_descuento = self.carrito_total() - self.get_discount()
        return max(total_con_descuento, Decimal(0))