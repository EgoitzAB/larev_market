from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib import messages
from .models import Direccion
from pagos.models import Orden, ItemOrden
from .forms import DireccionForm
from carrito.carrito import Carrito
from django.shortcuts import redirect

def checkout(request):
    carrito = Carrito(request)
    direcciones = None

    # Verificar si el carrito está vacío
    if not carrito:
        messages.warning(request, "Tu carrito está vacío. Por favor, añade productos antes de proceder al checkout.")
        return redirect('tienda:home')  # Redirigir a la página de inicio
    if request.user.is_authenticated:

        # Solo buscar direcciones si el usuario está autenticado
        direcciones = Direccion.objects.filter(usuario=request.user)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Redirigir al inicio de sesión si no está autenticado
            return redirect('account_login')  # Ajusta esta URL según tu configuración

        direccion_id = request.POST.get('direccion_id')
        direccion = None

        if direccion_id:
            # Obtiene la dirección seleccionada por el usuario
            direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
        else:
            # Si no seleccionó una dirección existente, intenta crear una nueva
            direccion_form = DireccionForm(request.POST)
            if direccion_form.is_valid():
                direccion = direccion_form.save(commit=False)
                direccion.usuario = request.user
                direccion.save()
            else:
                # Devuelve el formulario con errores si no es válido
                return render(request, 'checkout/checkout.html', {
                    'form': direccion_form,
                    'carrito': carrito,
                    'direcciones': direcciones,
                })


        try:
            # Crear la orden
            orden = Orden.crear_orden(cliente=request.user, direccion_envio=direccion, carrito=carrito)
            # Limpiar el carrito
            carrito.limpiar()
            # Redirigir al flujo de pago
            messages.success(request, "Orden creada correctamente. Procede al pago.")
            return redirect('pagos:realizar_compra', orden_id=orden.id)
        except Exception as e:
            # Manejar errores durante la creación de la orden
            messages.error(request, f"Error al crear la orden: {str(e)}")
            return redirect('checkout:crear_orden')

    else:
        # Mostrar el formulario de dirección
        direccion_form = DireccionForm()

    return render(request, 'checkout/checkout.html', {
        'form': direccion_form,
        'carrito': carrito,
        'direcciones': direcciones,
    })