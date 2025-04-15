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
            
            Pago.objects.create(orden=orden, estado="pendiente")

            # 🔹 Liberar stock en 10 minutos si el pago no se confirma
            # liberar_stock_en_10_minutos.apply_async(args=[orden.id], countdown=630)
            # Pago exitoso, stock ya ha sido reducido
            request.session.set_expiry(670)  # Expira en 60 segundos
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
def confirmacion_compra(request, orden_id):
    """Verifica el estado de la transacción y maneja la confirmación de la compra"""
    logging.info(f"Confirmación de compra iniciada para la orden_id: {orden_id}.")
    try:
        compra = Orden.objects.get(id=orden_id, cliente=request.user)
        logging.info(f"Orden encontrada: {compra.id}, estado actual: {compra.estado}.")
    except Orden.DoesNotExist:
        logging.error(f"Orden no encontrada para orden_id: {orden_id}.")
        messages.error(request, "Orden no encontrada.")
        return redirect('compra:carrito')

    # Obtener el estado de la transacción
    transaction_status = request.GET.get("status")  # "status" debería ser el estado de la transacción de PayGreen
    logging.info(f"Estado de la transacción recibido: {transaction_status}.")
    # Extraemos los datos del diccionario de la respuesta de PayGreen (en caso de estar disponibles)
    po_id = request.GET.get("po_id")
    if po_id:
        logging.info(f"ID de la orden de pago recibido de PayGreen: {po_id}")
        # Asegúrate de hacer una consulta a la API de PayGreen si necesitas más datos
        # Simulamos que hemos obtenido estos datos como ejemplo:
        # response_data = obtener_datos_de_paygreen(po_id)  # Ejemplo de función que puede traer más detalles
        # transaction_status = response_data['status']  # Suponiendo que 'status' venga de la API

    if transaction_status == "captured" or transaction_status == "successed":
        # Pago capturado exitosamente
        compra.estado = "completada"
        compra.save()
        logging.info(f"Pago capturado exitosamente. Estado de la compra actualizado a: {compra.estado}.")

        if compra.pago:
            pago = compra.pago
            pago.estado = "exitoso"
            pago.save()
            logging.info(f"Estado del pago actualizado a 'exitoso' para la orden {compra.id}.")

        messages.success(request, "Pago exitoso. ¡Gracias por tu compra!")
        return render(request, 'pagos/confirmacion.html', {'compra': compra})

    elif transaction_status == "authorized":
        # Pago autorizado pero no capturado
        compra.estado = "pendiente"
        compra.save()
        logging.info(f"Pago autorizado. Estado de la compra actualizado a: {compra.estado}.")

        if compra.pago:
            pago = compra.pago
            pago.estado = "pendiente"
            pago.save()
            logging.info(f"Estado del pago actualizado a 'pendiente' para la orden {compra.id}.")

        messages.info(request, "El pago ha sido autorizado, pero aún no se ha capturado.")
        return render(request, 'pagos/pendiente.html', {'compra': compra})

    else:
        # Redirigir si el estado no es reconocido
        logging.warning(f"Estado de la transacción no reconocido: {transaction_status}. Redirigiendo a cancelación.")
        return redirect('pagos:cancelacion_compra', orden_id=compra.id)

@login_required
def cancelacion_compra(request, orden_id):
    """Maneja las cancelaciones de pagos: rechazados, expirados, errores, etc."""
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        messages.error(request, "Orden no encontrada.")
        return redirect('compra:carrito')

    # Aquí obtenemos el estado de la transacción desde PayGreen
    transaction_status = request.GET.get("status")  # 'status' de la respuesta de PayGreen

    # En función del estado de la transacción, actualizamos la orden y el pago
    if transaction_status in ["refused", "expired", "error", "canceled"]:
        # Si el pago fue rechazado, expiró, hubo un error, o fue cancelado
        orden.estado = "fallida"
        orden.save()

        if orden.pago:
            pago = orden.pago
            pago.estado = "fallido"
            pago.save()

        # Liberar el stock ya que no se realizó el pago
        liberar_stock(orden)

        messages.error(request, f"El pago fue {transaction_status}.")
    else:
        messages.error(request, "Estado del pago no reconocido.")

    return render(request, 'pagos/cancelacion.html', {'orden': orden})

def liberar_stock(orden):
    """Liberar el stock de los productos en la orden"""
    with transaction.atomic():
        for item in orden.items.all():
            item.producto.stock += item.cantidad
            item.producto.save()

@login_required
def confirmacion_recogida(request, orden_id):
    """
    Vista de confirmación para pedidos de recogida en tienda.
    Marca la orden como completada y muestra la confirmación sin pasar por el proceso de PayGreen.
    """
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        messages.error(request, "Orden no encontrada.")
        return redirect('compra:carrito')

    # Actualizar el estado de la orden a "completada"
    orden.estado = "completada"
    orden.save()

    # Si la orden posee un registro de pago, se actualiza el estado
    if hasattr(orden, 'pago'):
        orden.pago.estado = "exitoso"
        orden.pago.save()

    messages.success(request, "Orden confirmada. Recoge tu pedido en tienda y paga en efectivo al recogerlo.")
    return render(request, 'pagos/confirmacion_recogida.html', {'orden': orden})