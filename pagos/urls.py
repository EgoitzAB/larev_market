from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('iniciar/<int:orden_id>/', views.iniciar_pago, name='iniciar_pago'),
    path('exito/', views.pago_exito, name='pago_exito'),
    path('cancelado/', views.pago_cancelado, name='pago_cancelado'),
]
