from django.contrib import admin
from .models import Orden, ItemOrden, Pago

class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 1

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'total', 'estado')
    search_fields = ('cliente__username', 'id')
    list_filter = ('estado', 'fecha_creacion')
    inlines = [ItemOrdenInline]

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('orden', 'estado', 'fecha_pago', 'referencia')
    search_fields = ('orden__id', 'referencia')
    list_filter = ('estado', 'fecha_pago')

