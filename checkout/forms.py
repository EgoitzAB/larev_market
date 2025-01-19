from django import forms
from .models import Direccion

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre', 'apellido', 'direccion', 'ciudad', 'codigo_postal', 'provincia', 'pais', 'email', 'telefono', 'es_direccion_envio']
