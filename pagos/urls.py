from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('iniciar/<int:orden_id>/', views.realizar_compra, name='realizar_compra'),
    path('exito/<int:orden_id>/', views.confirmacion_compra, name='confirmacion_compra'),
    path('recogida/exito/<int:orden_id>/', views.confirmacion_recogida, name='confirmacion_recogida'),
    path('cancelado/<int:orden_id>/', views.cancelacion_compra, name='cancelacion_compra'),
    path('webhooks/paygreen/authorized/', views.PayGreenAuthorizedWebhook.as_view(), name='pg_authorized'),
    path('webhooks/paygreen/canceled/',  views.PayGreenCanceledWebhook.as_view(),  name='pg_canceled'),
]

