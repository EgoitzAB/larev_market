from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Direccion
from pagos.models import Orden
from .forms import DireccionForm
from carrito.carrito import Carrito
from django.http import JsonResponse

def checkout(request):
    carrito = Carrito(request)
    direcciones = None
    cupon = carrito.coupon  # Recuperamos el cupón aplicado desde el carrito
    descuento = 0  # Inicializamos el descuento

    if not carrito:
        messages.warning(request, "Tu carrito está vacío. Añade productos antes de proceder al checkout.")
        return redirect('tienda:home')

    # Si hay un cupón aplicado, obtenemos el descuento
    if cupon:
        descuento = carrito.get_discount()  # Usamos el método que devuelve el descuento

    if request.user.is_authenticated:
        direcciones = Direccion.objects.filter(usuario=request.user)

        if direcciones.count() >= 5:
            messages.warning(request, "Solo puedes guardar hasta 5 direcciones. Selecciona una existente.")

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')

        direccion_id = request.POST.get('direccion_id')
        direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user) if direccion_id else None

        # Si no hay dirección seleccionada y el usuario tiene menos de 5 direcciones guardadas, crear una nueva
        if not direccion and direcciones.count() < 5:
            direccion_form = DireccionForm(request.POST)
            if direccion_form.is_valid():
                direccion = direccion_form.save(commit=False)
                direccion.usuario = request.user
                direccion.save()
            else:
                return render(request, 'checkout/checkout.html', {
                    'form': direccion_form, 'carrito': carrito, 'direcciones': direcciones,
                })

        # Crear la orden
        try:
            orden = Orden.crear_orden(
                cliente=request.user,
                direccion_envio=direccion,
                carrito=carrito,
                coupon=cupon
            )

            carrito.limpiar()
            carrito.remove_coupon()  # Eliminar el cupón de la sesión después de usarlo
            messages.success(request, "Orden creada correctamente. Procede al pago.")
            return redirect('pagos:realizar_compra', orden_id=orden.id)
        except Exception as e:
            messages.error(request, f"Error al crear la orden: {str(e)}")
            return redirect('checkout')

    # Recuperamos el total con el descuento aplicado
    total_con_descuento = carrito.get_total_price_after_discount()  # Total con descuento

    return render(request, 'checkout/checkout.html', {
        'form': DireccionForm(),
        'carrito': carrito,
        'direcciones': direcciones,
        'cupon': cupon,
        'descuento': descuento,
        'total_con_descuento': total_con_descuento,  # Pasamos el total con descuento
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
