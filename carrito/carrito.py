from decimal import Decimal
from django.conf import settings
from tienda.models import Producto


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
        # store current applied coupon
#        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self):
        """
        Iterar sobre los productos y recuperarlos de la base de datos
        """
        product_ids = self.carrito.keys()
        # get the product objects and add them to the cart
        productos = Producto.objects.filter(id__in=product_ids)
        carrito = self.carrito.copy()
        for producto in productos:
            carrito[str(producto.id)]['producto'] = producto
        for item in carrito.values():
            item['precio'] = Decimal(item['precio'])
            item['precio_total'] = item['precio'] * item['cantidad']
            yield item

    def __len__(self):
        """
        Contar los items del carrito.
        """
        return sum(item['cantidad'] for item in self.carrito.values())

    def añadir(self, producto, cantidad=1, sobreescribir=False):
        """
        Añade un producto o actualiza su cantidad.
        """
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {'cantidad': 0,
                                    'precio': str(producto.precio)}
        if sobreescribir:
            self.carrito[producto_id]['cantidad'] = cantidad
        else:
            self.carrito[producto_id]['cantidad'] += cantidad
        self.save()

    def save(self):
        # marcar la sesión cómo modificada para qué funcione
        self.session.modified = True

    def eliminar(self, producto):
        """
        Eliminar un producto del carrito.
        """
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.save()

    def limpiar(self):
        # eliminar el carrito de la session
        del self.session[settings.CARRITO_SESSION_ID]
        self.save()

    def carrito_total(self):
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.carrito.values())

#    @property
 #   def coupon(self):
  #      if self.coupon_id:
   #         try:
    #            return Coupon.objects.get(id=self.coupon_id)
     #       except Coupon.DoesNotExist:
      #          pass
       # return None

#    def get_discount(self):
 #       if self.coupon:
  #          return (self.coupon.discount / Decimal(100)) \
   #             * self.get_total_price()
    #    return Decimal(0)

    #def get_total_price_after_discount(self):
     #   return self.get_total_price() - self.get_discount()
