from django.urls import path
from .views import HomeView

app_name = 'tienda'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
