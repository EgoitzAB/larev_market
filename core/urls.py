from django.urls import path
from .views import verify_email_mfa, InfoTiendaView, TerminosDeUsoView, PrivacidadView

app_name = 'core'

urlpatterns = [
    path('accounts/mfa/verify/', verify_email_mfa, name='verify_email_mfa'),
    path("sobre-nosotros/", InfoTiendaView.as_view(), name="tienda_info"),
    path('terminos-de-uso/', TerminosDeUsoView.as_view(), name='terminos_de_uso'),
    path('politica-de-privacidad/', PrivacidadView.as_view(), name='politica_de_privacidad'),
]