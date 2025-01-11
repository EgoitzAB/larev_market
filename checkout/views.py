from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Direccion
from pagos.models import Orden, ItemOrden
from .forms import DireccionForm
from carrito.carrito import Carrito

def checkout(request):
    carrito = Carrito(request)
    direcciones = Direccion.objects.filter(usuario=request.user)

    if request.method == 'POST':
        direccion_id = request.POST.get('direccion_id')
        if direccion_id:
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
                })

        # Crear la orden
        orden = Orden.objects.create(
            cliente=request.user,
            direccion_envio=direccion,
            total=carrito.carrito_total(),
            estado='pendiente',
        )

        # Crear los items de la orden
        for item in carrito:
            ItemOrden.objects.create(
                orden=orden,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
            )

        carrito.limpiar()
        return redirect('pagos:paygreen_iniciar_pago', orden_id=orden.id)

    else:
        direccion_form = DireccionForm()

    return render(
        request,
        'checkout/checkout.html',
        {
            'form': direccion_form,
            'carrito': carrito,
            'direcciones': direcciones,
        }
    )
