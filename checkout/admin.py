from django.contrib import admin
from .models import Direccion

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre', 'apellido', 'direccion', 'ciudad', 'pais', 'es_direccion_envio')
    search_fields = ('usuario__username', 'nombre', 'apellido', 'direccion', 'ciudad', 'pais')
    list_filter = ('pais', 'es_direccion_envio')

