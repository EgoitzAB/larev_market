from django.shortcuts import get_object_or_404, redirect
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
        context['mostrar_modal'] = not self.request.session.get('es_mayor_de_edad', False)
        return context

def verificar_edad(request):
    if request.method == "POST" and request.POST.get("edad_confirmada"):
        request.session['es_mayor_de_edad'] = True
        return redirect('tienda:home')  # Redirigir a la página principal
    return redirect('tienda:home')  # En caso de fallo, volver a la página

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
        # Si el `variante_id` está presente en la URL, buscar la variante específica
        if 'variante_id' in self.kwargs:
            return get_object_or_404(ProductoVariante, id=self.kwargs['variante_id'], producto__slug=self.kwargs['slug'], producto__is_active=True)
        
        # Si no, retornar el producto principal
        return get_object_or_404(Producto, slug=self.kwargs['slug'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el objeto actual (puede ser Producto o ProductoVariante)
        objeto = self.get_object()

        if isinstance(objeto, Producto):
            # Si es un producto principal, incluir sus variantes
            variantes = ProductoVariante.objects.filter(producto=objeto)
        else:
            # Si es una variante, incluir solo la variante seleccionada
            variantes = [objeto]

        # Crear el formulario para añadir al carrito
        formulario_carrito = CarritoAñadirProductoForm()

        # Obtener productos recomendados basados en el producto principal
        producto_principal = objeto.producto if isinstance(objeto, ProductoVariante) else objeto
        r = Recomendador()
        productos_recomendados = r.recomendar_productos_para([producto_principal], 4)

        # Agregar todos estos datos al contexto
        context.update({
            'formulario_carrito': formulario_carrito,
            'productos_recomendados': productos_recomendados,
            'variantes': variantes,
            'producto_principal': producto_principal,
        })

        return context
