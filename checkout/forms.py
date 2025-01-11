from django import forms
from .models import Direccion

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre_completo', 'direccion', 'ciudad', 'codigo_postal', 'pais', 'telefono', 'es_direccion_envio']
