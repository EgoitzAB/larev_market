from django.db import models
from django.conf import settings
from tienda.models import ProductoVariante


class InfoTienda(models.Model):
    nombre_tienda = models.CharField(max_length=255, default="La Revolución Verde CBD")
    descripcion = models.TextField(
        help_text="Breve descripción de la tienda y sus valores.", 
        default="La Revolución Verde CBD es una destacada tienda especializada en productos derivados del cáñamo."
    )
    mision = models.TextField(
        help_text="La misión de la tienda.", 
        default="Nuestro compromiso es proporcionar productos que promuevan el bienestar y la salud."
    )
    vision = models.TextField(
        help_text="La visión de la tienda.",
        default="Creemos en los beneficios del CBD y nos esforzamos por educar a nuestra comunidad."
    )
    ubicaciones = models.TextField(
        help_text="Lista de ubicaciones en formato JSON. Ejemplo: [{'ciudad': 'Donostia', 'direccion': 'Calle San Francisco 54'}]",
        default='[{"ciudad": "Donostia-San Sebastián", "direccion": "Calle San Francisco 54"}, {"ciudad": "Vitoria-Gasteiz", "direccion": "Centro Comercial Dendaraba, local 5"}]'
    )

    def __str__(self):
        return self.nombre_tienda
