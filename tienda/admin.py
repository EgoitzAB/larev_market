from django.utils.html import format_html
from django.contrib import admin
from .models import Categoria, Producto, ProductoVariante


# Configuración del modelo de categorías
@admin.register(Categoria)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'thumbnail')  # Agregamos el thumbnail a la vista
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

    @admin.display(description="Imagen")
    def thumbnail(self, obj):
        if obj.imagen:
            return format_html(f'<img src="{obj.imagen.url}" style="width: 50px; height: auto;" />')
        return "Sin imagen"


# Inline para gestionar variantes dentro del producto
class ProductoVarianteInline(admin.TabularInline):
    model = ProductoVariante
    extra = 1  # Número de variantes adicionales visibles por defecto
    fields = ('nombre', 'sku', 'precio', 'stock', 'peso', 'talla', 'thumbnail')
    readonly_fields = ('sku', 'thumbnail')  # El SKU y la miniatura son de solo lectura

    @admin.display(description="Imagen")
    def thumbnail(self, obj):
        if obj.imagen1:
            return format_html(f'<img src="{obj.imagen1.url}" style="width: 50px; height: auto;" />')
        return "Sin imagen"


# Configuración del modelo de productos
@admin.register(Producto)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'is_active', 'created_at', 'updated_at', 'thumbnail')
    list_filter = ('categoria', 'is_active')
    search_fields = ('nombre', 'descripcion')
    inlines = [ProductoVarianteInline]
    ordering = ('-created_at',)

    @admin.display(description="Imagen")
    def thumbnail(self, obj):
        if obj.imagen1:
            return format_html(f'<img src="{obj.imagen1.url}" style="width: 50px; height: auto;" />')
        return "Sin imagen"


# Configuración del modelo de variantes (opcional, si quieres gestionarlas aparte)
@admin.register(ProductoVariante)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'producto', 'precio', 'stock', 'peso', 'talla', 'thumbnail')
    list_filter = ('producto__categoria',)
    search_fields = ('nombre', 'sku')

    @admin.display(description="Imagen")
    def thumbnail(self, obj):
        if obj.imagen1:
            return format_html(f'<img src="{obj.imagen1.url}" style="width: 50px; height: auto;" />')
        return "Sin imagen"
