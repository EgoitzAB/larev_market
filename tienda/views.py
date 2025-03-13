from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Categoria, Producto, ProductoVariante, Subcategoria
from carrito.forms import CarritoAñadirProductoForm
from .recomendador import Recomendador
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q

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
        categoria_slug = self.kwargs.get('categoria_slug')
        subcategoria_slug = self.kwargs.get('subcategoria_slug')
        
        if categoria_slug:
            categoria = get_object_or_404(Categoria, slug=categoria_slug)
            queryset = queryset.filter(categoria=categoria)
            
            if subcategoria_slug:
                subcategoria = get_object_or_404(Subcategoria, slug=subcategoria_slug, categoria=categoria)
                queryset = queryset.filter(subcategoria=subcategoria)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener la categoría y subcategoría actual
        categoria_slug = self.kwargs.get('categoria_slug')
        subcategoria_slug = self.kwargs.get('subcategoria_slug')
        
        if categoria_slug:
            categoria = get_object_or_404(Categoria, slug=categoria_slug)
            context['categoria'] = categoria
            context['subcategorias'] = Subcategoria.objects.filter(categoria=categoria)
            
            if subcategoria_slug:
                subcategoria = get_object_or_404(Subcategoria, slug=subcategoria_slug, categoria=categoria)
                context['subcategoria'] = subcategoria
        
        # Obtener todas las categorías para mostrarlas en el navbar o menú lateral
        context['categorias'] = Categoria.objects.all()
        
        return context


class ProductoDetalleView(DetailView):
    model = Producto
    template_name = 'tienda/detalle.html'

    def get_object(self):
        # Si se selecciona una variante específica
        if 'variante_id' in self.kwargs:
            return get_object_or_404(
                ProductoVariante,
                id=self.kwargs['variante_id'],
                producto__slug=self.kwargs['slug'],
                producto__is_active=True
            )
        # Si no, devolver el producto principal
        return get_object_or_404(Producto, slug=self.kwargs['slug'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el objeto actual
        objeto = self.get_object()

        # Si el objeto es un producto principal, listar todas sus variantes
        if isinstance(objeto, Producto):
            variantes = ProductoVariante.objects.filter(producto=objeto)
        else:
            # Si es una variante, solo incluir esta variante
            variantes = [objeto]

        # Obtener el producto principal para siempre mostrar su descripción
        producto_principal = objeto.producto if isinstance(objeto, ProductoVariante) else objeto

        # Obtener productos recomendados
        r = Recomendador()
        productos_recomendados = r.recomendar_productos_para([producto_principal], 4)

        context.update({
            'producto_principal': producto_principal,
            'variantes': variantes,
            'objeto': objeto,  # Esto puede ser el producto o una variante
            'es_variante': isinstance(objeto, ProductoVariante),
            'productos_recomendados': productos_recomendados,
        })

        return context

def buscar_productos_y_variantes(query, umbral=0.3):
    """
    Busca productos y variantes que coincidan con la consulta.
    :param query: Término de búsqueda.
    :param umbral: Umbral de similitud para TrigramSimilarity (por defecto 0.3).
    :return: Lista de productos y variantes ordenados por relevancia.
    """

    query = str(query)
    # Búsqueda en Producto
    productos = Producto.objects.annotate(
        similitud_nombre=TrigramSimilarity('nombre', query),
        similitud_descripcion=TrigramSimilarity('descripcion', query),
    ).filter(
        Q(similitud_nombre__gt=umbral) | Q(similitud_descripcion__gt=umbral)
    ).order_by('-similitud_nombre', '-similitud_descripcion')

    # Búsqueda en ProductoVariante
    variantes = ProductoVariante.objects.annotate(
        similitud_nombre=TrigramSimilarity('nombre', query),
    ).filter(
        Q(similitud_nombre__gt=umbral)
    ).order_by('-similitud_nombre')

    # Combinar resultados
    resultados = list(productos) + list(variantes)
    resultados.sort(key=lambda x: getattr(x, 'similitud_nombre', 0), reverse=True)

    return resultados

def buscar(request):
    query = request.GET.get('q', '')  # Obtener el término de búsqueda desde la URL
    resultados = []

    if query:
        resultados = buscar_productos_y_variantes(query)

    return render(request, 'tienda/resultados_busqueda.html', {
        'resultados': resultados,
        'query': query,
    })