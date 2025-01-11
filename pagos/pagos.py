import requests
from django.conf import settings

def iniciar_transaccion(orden):
    """
    Inicia una transacción con PayGreen.
    """
    url = f"{settings.PAYGREEN_ENDPOINT}/transactions"
    headers = {
        'Authorization': f"Bearer {settings.PAYGREEN_PRIVATE_KEY}",
        'Content-Type': 'application/json'
    }

    datos = {
        'amount': int(orden.total * 100),  # Convertir a centavos
        'currency': 'EUR',
        'order_id': orden.id,
        'return_url': 'https://tu-dominio.com/pagos/exito/',
        'cancel_url': 'https://tu-dominio.com/pagos/cancelado/',
        'customer': {
            'email': orden.cliente.email
        }
    }

    respuesta = requests.post(url, json=datos, headers=headers)
    respuesta.raise_for_status()
    return respuesta.json()  # Retorna los datos de la transacción
