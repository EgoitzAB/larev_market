from django import forms
from django.core.exceptions import ValidationError
from .models import Direccion
from django.conf import settings

import requests
import logging

logger = logging.getLogger(__name__)

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre', 'apellido', 'direccion', 'ciudad', 'codigo_postal', 
                  'provincia', 'pais', 'email', 'telefono', 'es_direccion_envio']

    def clean_direccion(self):
        """
        Valida que la dirección sea real utilizando la API de Google Maps.
        """
        # Obtén los datos del formulario
        direccion = self.cleaned_data.get('direccion')
        ciudad = self.cleaned_data.get('ciudad')
        codigo_postal = self.cleaned_data.get('codigo_postal')
        provincia = self.cleaned_data.get('provincia')
        pais = self.cleaned_data.get('pais')

        # Construye la dirección completa
        direccion_completa = f"{direccion}, {ciudad}, {provincia}, {codigo_postal}, {pais}"

        # Llama a la API de Google Maps Geocoding
        api_key = settings.GOOGLE_MAPS_API_KEY
        if not api_key:
            raise ValidationError("Error de configuración: No se encontró la API Key de Google Maps.")
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion_completa}&key={api_key}"
        
        try:
            # Realiza la solicitud a la API
            response = requests.get(url)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
            data = response.json()

            # Logging para depurar la respuesta de la API
            logger.debug(f"Respuesta de Google Maps API: {data}")

            # Verifica si la dirección es válida
            if data['status'] != 'OK':
                raise ValidationError("La dirección no es válida. Por favor, ingresa una dirección real.")

        except requests.exceptions.RequestException as e:
            # Maneja errores de conexión o de la API
            logger.error(f"Error al validar la dirección: {str(e)}")
            raise ValidationError("Error al validar la dirección. Por favor, inténtalo de nuevo más tarde.")

        return direccion