from django.urls import path
from .views import *

app_name = 'tienda'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('productos/', CategoriasView.as_view(), name='listado_producto'),
    path('productos/<slug:slug>/', ProductoDetalleView.as_view(), name='detalle_producto'),
    path('verificar-edad/', verificar_edad, name='verificar_edad'),
]
