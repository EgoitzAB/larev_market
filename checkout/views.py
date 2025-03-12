from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib import messages
from .models import Direccion
from pagos.models import Orden, ItemOrden
from .forms import DireccionForm
from carrito.carrito import Carrito
from django.shortcuts import redirect
from django.http import JsonResponse

import logging


logger = logging.getLogger(__name__)

def checkout(request):
    carrito = Carrito(request)
    direcciones = None

    # Verificar si el carrito está vacío
    if not carrito:
        messages.warning(request, "Tu carrito está vacío. Por favor, añade productos antes de proceder al checkout.")
        logger.warning("El carrito está vacío.")
        return redirect('tienda:home')  # Redirigir a la página de inicio

    if request.user.is_authenticated:
        # Solo buscar direcciones si el usuario está autenticado
        direcciones = Direccion.objects.filter(usuario=request.user)
        logger.info(f"Direcciones encontradas: {direcciones.count()}")

        # Limitar el número de direcciones a 5, pero permitir seleccionar una existente
        if direcciones.count() >= 5:
            messages.warning(request, "Solo puedes tener un máximo de 5 direcciones guardadas. Selecciona una de las direcciones existentes para continuar.")
            logger.warning("El usuario ya tiene 5 direcciones.")
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Redirigir al inicio de sesión si no está autenticado
            logger.warning("El usuario no está autenticado.")
            return redirect('account_login')  # Ajusta esta URL según tu configuración

        direccion_id = request.POST.get('direccion_id')
        direccion = None

        if direccion_id:
            # Obtiene la dirección seleccionada por el usuario
            direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
            logger.info(f"Dirección seleccionada: {direccion.id}")
        else:
            # Si no seleccionó una dirección existente, intenta crear una nueva
            if direcciones.count() < 5:  # Permitir agregar solo si hay menos de 5 direcciones
                direccion_form = DireccionForm(request.POST)
                if direccion_form.is_valid():
                    direccion = direccion_form.save(commit=False)
                    direccion.usuario = request.user
                    direccion.save()
                    logger.info(f"Dirección nueva guardada: {direccion.id}")
                else:
                    # Devuelve el formulario con errores si no es válido
                    logger.warning("El formulario de dirección no es válido.")
                    return render(request, 'checkout/checkout.html', {
                        'form': direccion_form,
                        'carrito': carrito,
                        'direcciones': direcciones,
                    })
            else:
                # Si ya tiene 5 direcciones, solo permite la selección de una existente
                messages.warning(request, "Ya tienes 5 direcciones guardadas. Selecciona una para continuar.")
                logger.warning("El usuario tiene 5 direcciones, no se permite agregar una nueva.")
                return render(request, 'checkout/checkout.html', {
                    'carrito': carrito,
                    'direcciones': direcciones,
                })

        try:
            # Crear la orden
            orden = Orden.crear_orden(cliente=request.user, direccion_envio=direccion, carrito=carrito)
            logger.info(f"Orden creada con ID: {orden.id}")

            # Limpiar el carrito
            carrito.limpiar()
            # Redirigir al flujo de pago
            messages.success(request, "Orden creada correctamente. Procede al pago.")
            return redirect('pagos:realizar_compra', orden_id=orden.id)
        except Exception as e:
            # Manejar errores durante la creación de la orden
            messages.error(request, f"Error al crear la orden: {str(e)}")
            logger.error(f"Error al crear la orden: {str(e)}")
            return redirect('checkout')

    else:
        # Mostrar el formulario de dirección
        direccion_form = DireccionForm()

    return render(request, 'checkout/checkout.html', {
        'form': direccion_form,
        'carrito': carrito,
        'direcciones': direcciones,
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
