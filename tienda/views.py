import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import Categoria, Producto, ProductoVariante
from carrito.forms import CarritoAñadirProductoForm
from .recomendador import Recomendador


class HomeView(TemplateView):
    template_name = "tienda/home.html"

    def get_context_data(self, **kwargs):
        """
        Sobrescribe el método para añadir datos al contexto del template.
        """
        context = super().get_context_data(**kwargs)

        # Prefetch de categorías, productos y variantes en una sola consulta
        categorias = Categoria.objects.prefetch_related(
            'productos__variantes'
        )

        # Construir un JSON-like dict con todas las categorías, productos y variantes
        productos_por_categoria = {
            categoria.nombre: [
                {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'descripcion': producto.descripcion,
                    'imagen1': producto.imagen1.url if producto.imagen1 else None,
                    'variantes': [
                        {
                            'id': variante.id,
                            'nombre': variante.nombre,
                            'precio': str(variante.precio),
                            'stock': variante.stock,
                            'peso': variante.peso,
                            'talla': variante.talla,
                            'imagen1': variante.get_imagen1().url if variante.get_imagen1() else None,
                            'imagen2': variante.get_imagen2().url if variante.get_imagen2() else None,
                        }
                        for variante in producto.variantes.all()
                    ]
                }
                for producto in categoria.productos.filter(is_active=True)
            ]
            for categoria in categorias
        }

        # Serializar productos_por_categoria como JSON para el template
        context['productos_por_categoria_json'] = productos_por_categoria
        
        return context


class CategoriasView(ListView):
    model = Producto
    template_name = 'tienda/listado.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Obtener la categoría seleccionada del parámetro 'categoria' en la URL
        categoria_seleccionada = self.request.GET.get('categoria')
        
        if categoria_seleccionada:
            categoria = get_object_or_404(Categoria, nombre=categoria_seleccionada)
            queryset = queryset.filter(categoria=categoria)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las categorías para mostrarlas en el navbar o menú lateral
        context['categorias'] = Categoria.objects.all()
        
        return context


class ProductoDetalleView(DetailView):
    model = Producto
    template_name = 'tienda/detalle.html'
    
    def get_object(self):
        # Filtrar el producto por su slug y solo mostrar los productos activos
        return get_object_or_404(Producto, slug=self.kwargs['slug'], is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el producto actual
        producto = self.get_object()

        # Obtener las variantes del producto, si las hay
        variantes = ProductoVariante.objects.filter(producto=producto)

        # Crear el formulario para añadir al carrito
        formulario_carrito = CarritoAñadirProductoForm()

        # Obtener productos recomendados (suponiendo que tienes un sistema de recomendaciones)
        r = Recomendador()
        productos_recomendados = r.recomendar_productos_para([producto], 4)

        # Agregar todos estos datos al contexto
        context.update({
            'formulario_carrito': formulario_carrito,
            'productos_recomendados': productos_recomendados,
            'variantes': variantes,
        })

        return context