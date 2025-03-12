import os
import json
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tienda.models import Categoria, Producto, ProductoVariante
from django.conf import settings
import uuid
import random

class Command(BaseCommand):
    help = "Carga los datos de Instagram en la base de datos."

    def handle(self, *args, **kwargs):
        # Ruta al archivo JSON
        json_file = "productos_instagram.json"
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"El archivo {json_file} no existe."))
            return

        # Leer el archivo JSON
        with open(json_file, "r", encoding="utf-8") as f:
            productos_data = json.load(f)

        # Procesar cada producto
        for producto_data in productos_data:
            try:
                # Obtener o crear la categoría
                categoria_nombre = producto_data.get("categoria", "Otros")
                categoria, created = Categoria.objects.get_or_create(
                    nombre=categoria_nombre,
                    defaults={'nombre': categoria_nombre}
                )
                nombre = producto_data.get("descripcion", "Producto sin nombre")[:200]  # Limitar a 200 caracteres
                producto = Producto(
                    nombre=nombre,
                    categoria=categoria,
                    descripcion=producto_data.get("descripcion", ""),
                )

                # Guardar el producto
                producto.save()

                # Subir la imagen (si existe)
                imagen_path = producto_data.get("imagen")
                if imagen_path:
                    # Construir la ruta completa de la imagen usando MEDIA_ROOT
                    ruta_imagen = os.path.join(settings.MEDIA_ROOT, "imagenes_descargadas", os.path.basename(imagen_path))
                    
                    print(f"Buscando imagen en: {ruta_imagen}")  # Verificar la ruta en la consola
                    
                    if os.path.exists(ruta_imagen):
                        with open(ruta_imagen, "rb") as img_file:
                            producto.imagen1.save(
                                os.path.basename(ruta_imagen),  # Nombre del archivo
                                File(img_file),  # Contenido del archivo
                                save=True  # Guardar el producto después de asignar la imagen
                            )
                        self.stdout.write(self.style.SUCCESS(f"Imagen subida para {producto.nombre}."))
                    else:
                        self.stdout.write(self.style.WARNING(f"No se encontró la imagen en {ruta_imagen}."))
                else:
                    self.stdout.write(self.style.WARNING(f"No se especificó una imagen para {producto.nombre}."))
                    # Generar precio y stock aleatorios
                precio_aleatorio = round(random.uniform(10.00, 100.00), 2)  # Precio entre 10.00 y 100.00
                stock_aleatorio = random.randint(1, 50)  # Stock entre 1 y 50
                # Crear una variante de producto (opcional)
                variante = ProductoVariante(
                    producto=producto,
                    nombre="Variante 1",  # Cambia esto según tu necesidad
                    precio=precio_aleatorio,
                    stock=stock_aleatorio,
                )
                variante.save()

                self.stdout.write(self.style.SUCCESS(f"Producto '{producto.nombre}' creado con éxito."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al procesar la publicación: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS("Todos los datos han sido cargados."))