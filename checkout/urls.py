from django.urls import path
from . import views

app_name = 'checkout'  # Registrar el namespace 'checkout'

urlpatterns = [
    path('crear/', views.checkout, name='crear_orden'),  # URL para el checkout
]
