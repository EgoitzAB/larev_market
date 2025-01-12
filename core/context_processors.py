from tienda.models import Categoria

def productos_por_categoria(request):
    categorias = Categoria.objects.prefetch_related('productos__variantes')
    productos_por_categoria = {
        categoria.nombre: [
            {
                'id': producto.id,
                'nombre': producto.nombre,
                'slug': producto.slug,
                'descripcion': producto.descripcion,
                'imagen1': producto.imagen1.url if producto.imagen1 else None,
                'variantes': [
                    {
                        'id': variante.id,
                        'sku': variante.sku,
                        'nombre': variante.nombre,
                        'precio': str(variante.precio),
                        'stock': variante.stock,
                        'slug': variante.slug,
                        'peso': variante.peso,
                        'talla': variante.talla,
                        'imagen1': variante.get_imagen1().url if variante.get_imagen1() else None,
                    }
                    for variante in producto.variantes.all()
                ]
            }
            for producto in categoria.productos.filter(is_active=True)
        ]
        for categoria in categorias
    }
    return {'productos_por_categoria_json': productos_por_categoria}
