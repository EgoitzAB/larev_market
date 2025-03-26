from django.urls import path
from .views import *

app_name = 'tienda'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('productos/', CategoriasView.as_view(), name='listado_producto'),  # Listado general de productos
    path('productos/categoria/<slug:categoria_slug>/', CategoriasView.as_view(), name='listado_categoria'),  # Listado por categoría
    path('productos/categoria/<slug:categoria_slug>/<slug:subcategoria_slug>/', CategoriasView.as_view(), name='listado_subcategoria'),  # Listado por subcategoría
    path('productos/<slug:slug>/', ProductoDetalleView.as_view(), name='detalle_producto'),  # Detalle de producto
    path('productos/<slug:slug>/variante/<int:variante_id>/', ProductoDetalleView.as_view(), name='detalle_variante'),  # Detalle de variante
    path('buscar/', buscar, name='buscar'),  # Búsqueda de productos
]