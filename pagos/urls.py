from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('iniciar/<int:orden_id>/', views.realizar_compra, name='realizar_compra'),
    path('exito/<int:orden_id>/', views.confirmacion_compra, name='confirmacion_compra'),
    path('cancelado/<int:orden_id>/', views.cancelacion_compra, name='cancelacion_compra'),
]

