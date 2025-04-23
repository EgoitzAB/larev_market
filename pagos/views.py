from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Orden, Pago
from .paygreen import obtener_token_jwt, crear_comprador, crear_orden_pago
from django.contrib.auth.decorators import login_required
from django.db import transaction
import logging
from allauth.account.decorators import verified_email_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.views import View
from .utils import validate_paygreen_signature


# --------------- VISTA PRINCIPAL: REALIZAR COMPRA ---------------
@login_required
@verified_email_required
def realizar_compra(request, orden_id):
    try:
        with transaction.atomic():
            orden = Orden.objects.select_for_update().get(id=orden_id, cliente=request.user)

            # Verificar y apartar stock inmediatamente
            for item in orden.items.select_related('producto').select_for_update():
                producto = item.producto
                if producto.stock < item.cantidad:
                    return render(request, 'pagos/error.html', {
                        'error_message': f"Stock insuficiente para {producto.nombre}"
                    })
                producto.stock -= item.cantidad
                producto.save()

            orden.stock_reservado = True
            orden.save()

            # Preparar pago
            jwt_token = obtener_token_jwt()
            if not jwt_token:
                raise ValueError("Error al obtener token JWT")

            buy_id = crear_comprador(jwt_token, orden)
            if not buy_id:
                raise ValueError("Error al crear comprador en PayGreen")

            hosted_payment_url = crear_orden_pago(jwt_token, orden, buy_id)
            if not hosted_payment_url:
                raise ValueError("Error al crear orden de pago")

            Pago.objects.create(orden=orden, estado="pendiente")
            request.session.set_expiry(670)
            return redirect(hosted_payment_url)

    except Exception as e:
        logging.error(f"[realizar_compra] {e}", exc_info=True)
        return render(request, 'pagos/error.html', {'error_message': str(e)})


# --------------- WEBHOOK AUTORIZADO: CONFIRMAR PAGO ---------------
@method_decorator(csrf_exempt, name='dispatch')
class PayGreenAuthorizedWebhook(View):
    def post(self, request, *args, **kwargs):
        if (err := validate_paygreen_signature(request)):
            return err

        if request.headers.get('Authorization') != f"Bearer {settings.PAYGREEN_SECRET_KEY}":
            return HttpResponseBadRequest("Unauthorized")

        try:
            data = json.loads(request.body)
            order_id = int(data['merchantOrderId'])
        except Exception:
            return HttpResponseBadRequest("Malformed payload")

        with transaction.atomic():
            orden = get_object_or_404(Orden.objects.select_for_update(), pk=order_id)
            if orden.estado != 'completada':
                orden.estado = 'completada'
                orden.stock_reservado = False
                orden.save()
                if hasattr(orden, 'pago'):
                    orden.pago.estado = 'exitoso'
                    orden.pago.save()

        return HttpResponse("OK", status=200)


# --------------- WEBHOOK CANCELACIÓN: REPONER STOCK ---------------
@method_decorator(csrf_exempt, name='dispatch')
class PayGreenCanceledWebhook(View):
    def post(self, request, *args, **kwargs):
        if (err := validate_paygreen_signature(request)):
            return err

        if request.headers.get('Authorization') != f"Bearer {settings.PAYGREEN_SECRET_KEY}":
            return HttpResponseBadRequest("Unauthorized")

        try:
            data = json.loads(request.body)
            order_id = int(data['merchantOrderId'])
        except Exception:
            return HttpResponseBadRequest("Malformed payload")

        with transaction.atomic():
            orden = get_object_or_404(Orden.objects.select_for_update(), pk=order_id)
            if orden.estado not in ('fallida', 'cancelada') and orden.stock_reservado:
                # Repone solo si había reserva
                for item in orden.items.select_related('producto').select_for_update():
                    producto = item.producto
                    producto.stock += item.cantidad
                    producto.save()

                orden.estado = 'fallida'
                orden.stock_reservado = False
                orden.save()
                if hasattr(orden, 'pago'):
                    orden.pago.estado = 'fallido'
                    orden.pago.save()

        return HttpResponse("OK")


# --------------- CONFIRMACIÓN CLIENTE (SOLO DISPLAY) ---------------
@login_required
def confirmacion_compra(request, orden_id):
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        messages.error(request, "Orden no encontrada.")
        return redirect('compra:carrito')

    # Si la orden ya está completada por el webhook, solo mostrar
    if orden.estado == 'completada':
        return render(request, 'pagos/confirmacion.html', {'compra': orden})

    estado = request.GET.get("status")
    if estado in ("captured", "successed") and orden.estado != 'completada':
        # Fallback si el webhook no llegó antes
        if orden.stock_reservado:
            # El stock ya estaba apartado en realizar_compra
            orden.stock_reservado = False
        orden.estado = 'completada'
        orden.save()
        if orden.pago:
            orden.pago.estado = 'exitoso'
            orden.pago.save()
        messages.success(request, "Pago exitoso. ¡Gracias por tu compra!")
        return render(request, 'pagos/confirmacion.html', {'compra': orden})

    elif estado == "authorized" and orden.estado != 'completada':
        orden.estado = 'pendiente'
        orden.save()
        if orden.pago:
            orden.pago.estado = 'pendiente'
            orden.pago.save()
        messages.info(request, "Pago autorizado, pendiente de confirmación.")
        return render(request, 'pagos/pendiente.html', {'compra': orden})

    return redirect('pagos:cancelacion_compra', orden_id=orden.id)


# --------------- CANCELACIÓN MANUAL O FALLIDA (SOLO DISPLAY) ---------------
@login_required
def cancelacion_compra(request, orden_id):
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        messages.error(request, "Orden no encontrada.")
        return redirect('compra:carrito')

    # Si ya fue procesada por webhook, solo mostrar
    if orden.estado in ('fallida', 'cancelada'):
        return render(request, 'pagos/cancelacion.html', {'orden': orden})

    estado = request.GET.get("status")
    if estado in ["refused", "expired", "error", "canceled"] and orden.stock_reservado:
        # Repone stock si quedó reservado
        for item in orden.items.select_related('producto'):
            producto = item.producto
            producto.stock += item.cantidad
            producto.save()
        orden.stock_reservado = False

    if estado in ["refused", "expired", "error", "canceled"]:
        orden.estado = 'fallida'
        orden.save()
        if orden.pago:
            orden.pago.estado = 'fallido'
            orden.pago.save()
        messages.error(request, f"El pago fue {estado}.")
    else:
        messages.error(request, "Estado del pago no reconocido.")

    return render(request, 'pagos/cancelacion.html', {'orden': orden})


# --------------- CONFIRMACIÓN RECOGIDA EN TIENDA ---------------
@login_required
def confirmacion_recogida(request, orden_id):
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        messages.error(request, "Orden no encontrada.")
        return redirect('compra:carrito')

    # Solo marcar completada y limpiar reserva
    if orden.estado != 'completada':
        orden.estado = 'completada'
        orden.stock_reservado = False
        orden.save()
        if hasattr(orden, 'pago'):
            orden.pago.estado = 'exitoso'
            orden.pago.save()

    messages.success(request, "Orden confirmada. Recoge tu pedido en tienda y paga en efectivo al recogerlo.")
    return render(request, 'pagos/confirmacion_recogida.html', {'orden': orden})
