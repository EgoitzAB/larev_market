import requests
import logging
from django.conf import settings
from django.urls import reverse


def obtener_token_jwt():
    """Obtener el token JWT de PayGreen"""
    url = f"{settings.PAYGREEN_API_URL}/auth/authentication/{settings.PAYGREEN_SHOP_ID}/secret-key"
    headers = {"Authorization": settings.PAYGREEN_SECRET_KEY}
    print(url)
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", {}).get("token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al obtener el token JWT: {e}")
        return None

def crear_comprador(jwt, orden):
    """Crear un comprador en PayGreen"""
    buyer_url = f"{settings.PAYGREEN_API_URL}/payment/buyers"
    buyer_data = {
        "billing_address": {
            "city": orden.direccion_envio.ciudad,
            "country": orden.direccion_envio.pais,
            "line1": orden.direccion_envio.direccion,
            "postal_code": orden.direccion_envio.codigo_postal,
            "state": orden.direccion_envio.provincia,
        },
        "reference": f"{orden.cliente.username}",
        "first_name": orden.direccion_envio.nombre,
        "last_name": orden.direccion_envio.apellido,
        "email": orden.direccion_envio.email,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {jwt}",
    }

    try:
        response = requests.post(buyer_url, json=buyer_data, headers=headers)
        response.raise_for_status()  # Lanza error si la respuesta es 4xx/5xx
        return response.json().get("data", {}).get("id")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al crear el comprador en PayGreen: {e}")
        if response is not None:
            logging.error(f"Respuesta del servidor: {response.text}")
        return None

def crear_orden_pago(jwt, orden, buyer_id):
    """Crear una orden de pago en PayGreen"""
    paygreen_url = f"{settings.PAYGREEN_API_URL}/payment/payment-orders"
        # Generar las URLs dinámicamente
    return_url = f"{settings.SITE_URL}{reverse('pagos:confirmacion_compra', args=[orden.id])}"
    cancel_url = f"{settings.SITE_URL}{reverse('pagos:cancelacion_compra', args=[orden.id])}"
    payload = {
        "auto_capture": True,
        "buyer": buyer_id,
        "currency": "eur",
        "merchant_initiated": False,
        "mode": "instant",
        "partial_allowed": False,
        "amount": int(orden.total * 100),  # Convertir a céntimos
        "description": f"Orden número {orden.id} LRVCBD",
        "integration_mode": "hosted_fields",
        "reference": f"r{orden.id}",
        "return_url": return_url,
        "cancel_url": cancel_url,
        "shop_id": settings.PAYGREEN_SHOP_ID,
        "platforms": ["bank_card"],
    }

    # Log de los datos que se van a enviar
    logging.info(f"Enviando solicitud a PayGreen para crear la orden de pago: {paygreen_url}")
    logging.info(f"Payload de la solicitud: {payload}")


    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {jwt}",
    }
    logging.info(f"Encabezados de la solicitud: {headers}")
    try:
        response = requests.post(paygreen_url, json=payload, headers=headers)
        data = response.json()
        logging.info("Respuesta de PayGreen: %s", data)
        response.raise_for_status()
        return response.json().get("data", {}).get("hosted_payment_url")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al crear la orden de pago en PayGreen: {e}")
                # Log del detalle completo de la respuesta si está disponible
        if e.response:
            try:
                error_details = e.response.json()
                logging.error(f"Detalles de la respuesta de error: {error_details}")
            except ValueError:
                logging.error("No se pudo parsear la respuesta de error a JSON")

        return None