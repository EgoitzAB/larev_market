from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.carrito_detalle, name='carrito_detalle'),
    path('añadir/', views.carrito_añadir, name='carrito_añadir'),
    path('eliminar/<int:variante_id>/', views.carrito_eliminar, name='carrito_eliminar'),
    path('eliminar_todo/<int:variante_id>/', views.carrito_eliminar_todo, name='carrito_eliminar_todo'),
]
