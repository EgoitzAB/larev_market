import redis
from django.conf import settings
from .models import Producto


# connect to redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class Recomendador:
    def obtener_llave(self, id):
        return f'product:{id}:comprado_con'

    def productos_comprados(self, productos):
        producto_ids = [p.id for p in productos]
        for producto_id in producto_ids:
            for con_id in producto_ids:
                # conseguir los diferentes ids de los productos
                if producto_id != con_id:
                    # incrementar la puntucación de los productos comprados juntos
                    r.zincrby(self.obtener_llave(producto_id),
                            1,
                            con_id)

    def recomendar_productos_para(self, productos, max_results=6):
        producto_ids = [p.id for p in productos]
        if len(productos) == 1:
            # solo 1 producto
            sugerencias = r.zrange(
                            self.obtener_llave(producto_ids[0]),
                            0, -1, desc=True)[:max_results]
        else:
            # generar una llave temporal
            flat_ids = ''.join([str(id) for id in producto_ids])
            tmp_key = f'tmp_{flat_ids}'
            # multiple products, combine scores of all products
            # store the resulting sorted set in a temporary key
            keys = [self.obtener_llave(id) for id in producto_ids]
            r.zunionstore(tmp_key, keys)
            # eliminar los ids de los productos para los cuáles es la recomendación
            r.zrem(tmp_key, *producto_ids)
            # conseguir los ids y ordenarlos descendientemente
            sugerencias = r.zrange(tmp_key, 0, -1,
                                desc=True)[:max_results]
            # eliminar las claves temporales
            r.delete(tmp_key)
        sugerencia_productos_ids = [int(id) for id in sugerencias]
        # get suggested products and sort by order of appearance
        sugerencia_productos = list(Producto.objects.filter(id__in=sugerencia_productos_ids))
        sugerencia_productos.sort(key=lambda x: sugerencia_productos_ids.index(x.id))
        return sugerencia_productos

    def eliminar_comprados(self):
        for id in Producto.objects.values_list('id', flat=True):
            r.delete(self.obtener_llave(id))