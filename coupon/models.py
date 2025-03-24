from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   help_text="Porcentaje de descuento de 0 a 100")
    activo = models.BooleanField()

    def __str__(self):
        return self.code