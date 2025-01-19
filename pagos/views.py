from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Orden, Pago
from .paygreen import *
from django.contrib.auth.decorators import login_required
from django.db import transaction
import requests
from carrito.context_processors import carrito
import logging
from secrets import compare_digest
from allauth.account.decorators import verified_email_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@verified_email_required
@login_required
def realizar_compra(request, orden_id):
    """Crear la orden y manejar la redirección a la página de pago y la vuelta"""
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        return redirect('compra:carrito')

    # Verificar y reservar stock
    try:
        with transaction.atomic():
            # Reservar stock
            for item in orden.items.select_for_update():
                producto = item.producto
                cantidad = item.cantidad
                if producto.stock >= cantidad:
                    producto.stock -= cantidad
                    producto.save()
                else:
                    logging.error("Stock insuficiente para el producto %s", producto.id)
                    return render(request, 'pagos/error.html', {'error_message': f"Stock insuficiente para el producto {producto.nombre}"})

            # Stock reservado, proceder con el pago
            jwt_token = obtener_token_jwt()
            if not jwt_token:
                raise ValueError("Error al obtener el token JWT de PayGreen")

            try:
                buy_id = crear_comprador(jwt_token, orden)
                if not buy_id:
                    logging.error(
                        f"Error al crear el comprador en PayGreen para la orden {orden.id}. "
                        f"Token JWT: {jwt_token}, Datos de la orden: {orden}"
                    )
                    raise ValueError("No se recibió un ID de comprador válido al intentar crear el comprador en PayGreen.")
            except Exception as e:
                logging.error(
                    f"Excepción al intentar crear el comprador en PayGreen para la orden {orden.id}: {e}",
                    exc_info=True  # Esto incluye el traceback completo en los logs
                )
                raise ValueError("Error al crear el comprador en PayGreen. Revisa los logs para más detalles.")


            hosted_payment_url = crear_orden_pago(jwt_token, orden, buy_id)
            if not hosted_payment_url:
                raise ValueError("Error al crear la orden de pago en PayGreen")

            # Pago exitoso, stock ya ha sido reducido
            request.session.set_expiry(60)  # Expira en 60 segundos
            return redirect(hosted_payment_url)

    except ValueError as e:
        logging.error(str(e))
        return render(request, 'pagos/error.html', {'error_message': str(e)})
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al realizar la solicitud a PayGreen: {e}")
        return render(request, 'pagos/error.html', {'error_message': f"Error al realizar la solicitud a PayGreen: {e}"})
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return render(request, 'pagos/error.html', {'error_message': f"Error inesperado: {e}"})


@login_required
def confirmacion_compra(request, compra_id):
    compra = Orden.objects.get(id=compra_id)
    return render(request, 'pagos/confirmacion.html', {'compra': compra})


@login_required
def cancelacion_compra(request, compra_id):
    compra = Orden.objects.get(id=compra_id)
    return render(request, 'pagos/cancelacion.html', {'compra': compra})
