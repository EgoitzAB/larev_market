from django.views.generic import TemplateView
from .models import Categoria, Producto

class HomeView(TemplateView):
    template_name = "tienda/home.html"

    def get_context_data(self, **kwargs):
        """
        Sobrescribe el método para añadir datos al contexto del template.
        """
        context = super().get_context_data(**kwargs)
        # Obtener todas las categorías
        categorias = Categoria.objects.all()

        # Obtener las variantes agrupadas por categorías
        productos_por_categoria = {
            categoria.nombre: Producto.objects.filter(categoria=categoria).prefetch_related('variantes')
            for categoria in categorias
        }

        # Añadir datos al contexto
        context['categorias'] = categorias
        context['productos_por_categoria'] = productos_por_categoria
        return context
