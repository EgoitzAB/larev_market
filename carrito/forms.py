from django import forms


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CarritoAñadirProductoForm(forms.Form):
    cantidad = forms.TypedChoiceField(
                                choices=PRODUCT_QUANTITY_CHOICES,
                                coerce=int,
                                label='Cantidad')
    sobreescribir = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)
