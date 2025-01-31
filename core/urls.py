from django.urls import path
from .views import verify_email_mfa, InfoTiendaView, TerminosDeUsoView, PrivacidadView,\
    perfil, eliminar_favorito, detalle_orden, enviar_factura
from django.views.generic.base import TemplateView

app_name = 'core'

urlpatterns = [
    path('accounts/mfa/verify/', verify_email_mfa, name='verify_email_mfa'),
    path("sobre-nosotros/", InfoTiendaView.as_view(), name="tienda_info"),
    path('terminos-de-uso/', TerminosDeUsoView.as_view(), name='terminos_de_uso'),
    path('politica-de-privacidad/', PrivacidadView.as_view(), 
                                                    name='politica_de_privacidad'),
    path('perfil/', perfil, name='perfil'),
    path("robots.txt", TemplateView.as_view(template_name="core/robots.txt",
                                            content_type="text/plain")),
    path('eliminar-favorito/<int:favorito_id>/', eliminar_favorito, name='eliminar_favorito'),
    path('detalle-orden/<int:orden_id>/', detalle_orden, name='detalle_orden'),
    path('enviar_factura/<int:orden_id>/', enviar_factura, name='enviar_factura'),
]