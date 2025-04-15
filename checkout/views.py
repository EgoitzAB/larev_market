from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Direccion
from pagos.models import Orden
from .forms import DireccionForm
from carrito.carrito import Carrito
from django.http import JsonResponse
from django.conf import settings

def get_direccion_tienda():
    """
    Obtiene la dirección de la tienda (definida en settings).
    Si no existe, la crea usando los datos de settings.TIENDA_DIRECCION.
    """
    direccion_tienda = Direccion.objects.filter(es_direccion_tienda=True).first()
    if not direccion_tienda:
        datos = settings.TIENDA_DIRECCION
        # Si se permite usuario nulo para direcciones de tienda, se asigna None
        direccion_tienda = Direccion.objects.create(
            usuario=None,  # dirección global sin usuario
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido"),
            direccion=datos.get("direccion"),
            ciudad=datos.get("ciudad"),
            codigo_postal=datos.get("codigo_postal"),
            provincia=datos.get("provincia"),
            pais=datos.get("pais"),
            email=datos.get("email"),
            telefono=datos.get("telefono"),
            es_direccion_envio=True,
            es_direccion_tienda=True
        )
    return direccion_tienda


@login_required
def checkout(request):
    carrito = Carrito(request)
    direcciones = Direccion.objects.filter(usuario=request.user)
    cupon = carrito.coupon
    descuento = carrito.get_discount() if cupon else 0

    if not carrito:
        messages.warning(request, "Tu carrito está vacío. Añade productos antes de proceder al checkout.")
        return redirect('tienda:home')

    if direcciones.count() >= 3:
        messages.warning(request, "Solo puedes guardar hasta 3 direcciones. Selecciona una existente.")

    if request.method == 'POST':
        metodo_entrega = request.POST.get('metodo_entrega')
        metodo_pago = request.POST.get('metodo_pago')
        
        if metodo_entrega == 'recogida':
            nombre_cliente_recogida = request.POST.get('nombre_cliente_recogida')
            if not nombre_cliente_recogida:
                messages.error(request, "Debes ingresar tu nombre para la recogida en tienda.")
                return redirect('checkout:crear_orden')
            direccion = get_direccion_tienda()            
            if not direccion:
                messages.error(request, "No se ha configurado la dirección de la tienda.")
                return redirect('checkout:crear_orden')
            if metodo_pago == 'efectivo':
                orden = Orden.crear_orden(
                    cliente=request.user,
                    direccion_envio=direccion,
                    carrito=carrito,
                    coupon=cupon
                )
                carrito.limpiar()
                carrito.remove_coupon()
                messages.success(request, "Orden creada correctamente. Recoge tu pedido en tienda y paga en efectivo.")
                return redirect('pagos:confirmacion_recogida', orden_id=orden.id)
            elif metodo_pago == 'tarjeta':
                # Si es tarjeta, se procesa el pago normalmente usando PayGreen
                pass  # Continuar con el proceso abajo (ver bloque try)
            else:
                messages.error(request, "El método de pago no es válido para recogida en tienda.")
                return redirect('checkout:crear_orden')
        else:
            tipo_direccion = request.POST.get('tipo_direccion')
            if tipo_direccion == 'existente':
                direccion_id = request.POST.get('direccion_id')
                if not direccion_id:
                    messages.error(request, "Debes seleccionar una dirección existente.")
                    return redirect('checkout:crear_orden')
                direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
            else:
                direccion_form = DireccionForm(request.POST)
                if direccion_form.is_valid():
                    direccion = direccion_form.save(commit=False)
                    direccion.usuario = request.user
                    direccion.save()
                else:
                    return render(request, 'checkout/checkout.html', {
                        'form': direccion_form,
                        'carrito': carrito,
                        'direcciones': direcciones,
                        'cupon': cupon,
                        'descuento': descuento,
                    })
            if metodo_pago != 'tarjeta':
                messages.error(request, "El método de pago a domicilio es solo con tarjeta.")
                return redirect('checkout:crear_orden')

        try:
            orden = Orden.crear_orden(
                cliente=request.user,
                direccion_envio=direccion,
                carrito=carrito,
                coupon=cupon
            )
            carrito.limpiar()
            carrito.remove_coupon()
            messages.success(request, "Orden creada correctamente. Procede al pago.")
            return redirect('pagos:realizar_compra', orden_id=orden.id)
        except Exception as e:
            messages.error(request, f"Error al crear la orden: {str(e)}")
            return redirect('checkout:crear_orden')

    total_con_descuento = carrito.get_total_price_after_discount()

    return render(request, 'checkout/checkout.html', {
        'form': DireccionForm(),
        'carrito': carrito,
        'direcciones': direcciones,
        'cupon': cupon,
        'descuento': descuento,
        'total_con_descuento': total_con_descuento,
    })


def eliminar_direccion(request, direccion_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'No estás autenticado.'})

    # Obtener la dirección y asegurarse de que pertenece al usuario actual
    direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)

    try:
        direccion.delete()  # Eliminar la dirección
        return JsonResponse({'success': True, 'message': 'Dirección eliminada correctamente.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al eliminar la dirección: {str(e)}'})
