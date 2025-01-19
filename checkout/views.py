from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Direccion
from pagos.models import Orden, ItemOrden
from .forms import DireccionForm
from carrito.carrito import Carrito
from django.shortcuts import redirect

def checkout(request):
    carrito = Carrito(request)
    direcciones = None

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

        # Crear la orden utilizando el método del modelo Orden
        orden = Orden.crear_orden(cliente=request.user, direccion_envio=direccion, carrito=carrito)

        # Limpia el carrito después de crear la orden
        carrito.limpiar()

        # Redirige al flujo de pago
        return redirect('pagos:realizar_compra', orden_id=orden.id)

    else:
        direccion_form = DireccionForm()

    # Renderiza la vista del formulario de checkout
    return render(
        request,
        'checkout/checkout.html',
        {
            'form': direccion_form,
            'carrito': carrito,
            'direcciones': direcciones,
        }
    )
