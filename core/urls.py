from django.urls import path
from .views import verify_email_mfa

urlpatterns = [
    path('accounts/mfa/verify/', verify_email_mfa, name='verify_email_mfa'),
]