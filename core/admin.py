from django.contrib import admin
from .models import InfoTienda

@admin.register(InfoTienda)
class InfoTiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre_tienda',)
    fields = ('nombre_tienda', 'descripcion', 'mision', 'vision', 'ubicaciones')
