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
        # Ya no es necesario agregar 'productos_por_categoria_json' manualmente,
        # ya que se añadirá automáticamente desde el context processor
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