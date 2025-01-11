from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Orden, Pago
from .pagos import iniciar_transaccion

def iniciar_pago(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, cliente=request.user)

    if orden.estado != 'pendiente':
        messages.error(request, "La orden no está disponible para el pago.")
        return redirect('orden:detalle', orden_id=orden.id)

    try:
        # Inicia el pago con PayGreen
        transaccion = iniciar_transaccion(orden)
        pago = Pago.objects.create(
            orden=orden,
            estado='pendiente',
            referencia=transaccion.get('transaction_id')
        )
        # Redirigir al usuario a la URL de PayGreen
        return redirect(transaccion['payment_url'])

    except Exception as e:
        messages.error(request, f"Error al iniciar el pago: {e}")
        return redirect('orden:detalle', orden_id=orden.id)

def pago_exito(request):
    messages.success(request, "Pago realizado correctamente.")
    return render(request, 'pagos/exito.html')

def pago_cancelado(request):
    messages.warning(request, "El pago fue cancelado.")
    return render(request, 'pagos/cancelado.html')
