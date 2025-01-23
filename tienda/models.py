from django.db import models
from django.utils.text import slugify

import os
import uuid
from PIL import Image


class ImageOptimizableModel(models.Model):
    """
    Clase base que añade funcionalidad de optimización de imágenes a los modelos.
    """
    class Meta:
        abstract = True  # No se crea tabla en la base de datos para esta clase

    def optimize_image(self, image_field):
        """
        Optimiza la imagen especificada en el campo proporcionado.
        """
        if not image_field or not image_field.path:
            return

        try:
            with Image.open(image_field.path) as img:
                img = img.convert("RGB")
                max_dimension = 980
                img.thumbnail((max_dimension, max_dimension))
                new_image_path = os.path.splitext(image_field.path)[0] + ".webp"
                img.save(new_image_path, format="WebP", optimize=True, quality=75)
                image_field.name = os.path.basename(new_image_path)
        except Exception as e:
            print(f"Error optimizando imagen: {e}")


# Categorías
class Categoria(ImageOptimizableModel):
    """
    Categorías para los productos, como 'Flores', 'Resina', 'Ropa', etc.
    """
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    imagen = models.ImageField(
        upload_to="categorias/",
        null=True,
        blank=True,
        help_text="Imagen de la categoría (se optimizará automáticamente)."
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
        self.optimize_image(self.imagen)


# Productos
class Producto(ImageOptimizableModel):
    """
    Productos principales, como 'Flores Lemon Haze', 'Camiseta de Cáñamo', etc.
    """
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
        help_text="Categoría a la que pertenece el producto."
    )
    descripcion = models.TextField(blank=True, help_text="Descripción del producto.")
    imagen1 = models.ImageField(
        upload_to="productos/",
        null=True,
        blank=True,
        help_text="Primera imagen del producto (se optimizará automáticamente)."
    )
    imagen2 = models.ImageField(
        upload_to="productos/",
        null=True,
        blank=True,
        help_text="Segunda imagen del producto (opcional)."
    )
    
    is_active = models.BooleanField(default=True, help_text="Definir si el producto está activo o no.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
        self.optimize_image(self.imagen1)
        self.optimize_image(self.imagen2)


# Variantes (opcional por peso, talla, etc.)
class ProductoVariante(ImageOptimizableModel):
    """
    Variantes de producto, como peso, talla o formato.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="variantes",
        help_text="Producto principal al que pertenece esta variante."
    )
    sku = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100, help_text="Nombre de la variante, e.g., 'Lemon Haze 5g'.")
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de esta variante.")
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad en stock.")
    slug = models.SlugField(unique=True, blank=True, null=True)
    peso = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Peso en gramos, si aplica (para flores o resina)."
    )
    talla = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Talla, si aplica (para ropa)."
    )

    imagen1 = models.ImageField(
        upload_to="variantes/",
        null=True,
        blank=True,
        help_text="Imagen de la variante (opcional, se usa si no hay imagen del producto)."
    )

    imagen2 = models.ImageField(
        upload_to="variantes/",
        null=True,
        blank=True,
        help_text="Imagen de la variante (opcional, se usa si no hay imagen del producto)."
    )

    def __str__(self):
        return f"{self.producto.nombre} - {self.nombre}"
    
    def get_imagen1(self):
        # Si la variante tiene imagen, la devuelve. Si no, devuelve la imagen del producto
        if self.imagen1:
            return self.imagen1
        return self.producto.imagen1

    def get_imagen2(self):
        if self.imagen2:
            return self.imagen2
        return self.producto.imagen2
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.producto.nombre}-{self.nombre}")
        super().save(*args, **kwargs)
        self.optimize_image(self.imagen1)
        self.optimize_image(self.imagen2)


    class Meta:
        verbose_name = "Variante de producto"
        verbose_name_plural = "Variantes de producto"
        unique_together = ('producto', 'slug')