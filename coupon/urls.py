from django.urls import path
from . import views

app_name = 'coupon'

urlpatterns = [
    path('usar/', views.coupon_apply, name='apply'),
]