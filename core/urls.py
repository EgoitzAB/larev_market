from django.urls import path
from .views import verify_email_mfa, InfoTiendaView, TerminosDeUsoView, PrivacidadView,\
    perfil, detalle_orden, enviar_factura, toggle_favorito, guardar_favoritos
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
    path('toggle-favorito/', toggle_favorito, name='toggle_favorito'),
    path('guardar-favoritos/', guardar_favoritos, name='guardar_favoritos'),    path('detalle-orden/<int:orden_id>/', detalle_orden, name='detalle_orden'),
    path('enviar_factura/<int:orden_id>/', enviar_factura, name='enviar_factura'),
]