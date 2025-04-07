from django import forms
from django.core.exceptions import ValidationError
from localflavor.es.es_provinces import PROVINCE_CHOICES
from localflavor.es.forms import ESProvinceSelect
from .models import Direccion
from django.conf import settings
from django_countries.fields import CountryField  # Para manejar países
import requests
import logging
import phonenumbers  # Para validar el teléfono

logger = logging.getLogger(__name__)

class DireccionForm(forms.ModelForm):
    pais = CountryField().formfield()  # Campo de país con django-countries
    provincia = forms.ChoiceField(choices=PROVINCE_CHOICES, widget=ESProvinceSelect())  # Provincias de España con selector    print(provincia)

    class Meta:
        model = Direccion
        fields = ['nombre', 'apellido', 'direccion', 'ciudad', 'codigo_postal', 
                  'provincia', 'pais', 'email', 'telefono', 'es_direccion_envio']

    def clean_telefono(self):
        """
        Valida que el número de teléfono sea válido.
        """
        telefono = self.cleaned_data.get('telefono')
        pais = self.cleaned_data.get('pais')

        if telefono and pais:
            try:
                # Parsear el número de teléfono con el código de país
                parsed_phone = phonenumbers.parse(telefono, pais)
                if not phonenumbers.is_valid_number(parsed_phone):
                    raise ValidationError("El número de teléfono no es válido para el país seleccionado.")
            except phonenumbers.NumberParseException as e:
                raise ValidationError(f"Error al validar el teléfono: {str(e)}")

        return telefono

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

    def clean(self):
        """
        Validación adicional para el formulario completo.
        """
        cleaned_data = super().clean()

        # Verifica que el código postal sea válido (ejemplo para España)
        codigo_postal = cleaned_data.get('codigo_postal')
        pais = cleaned_data.get('pais')

        if pais and pais == 'ES' and codigo_postal:
            if not codigo_postal.isdigit() or len(codigo_postal) != 5:
                raise ValidationError({'codigo_postal': 'El código postal no es válido para España.'})

        return cleaned_data