from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from tienda.models import Producto, ProductoVariante
from coupon.forms import CouponApplyForm
from coupon.models import Coupon
from tienda.recomendador import Recomendador
from .carrito import Carrito
from .forms import CarritoAñadirProductoForm


@require_POST
def carrito_añadir(request):
    carrito = Carrito(request)
    variante_id = request.POST['variante_id']

    if not variante_id:
        messages.error(request, "Debes seleccionar una variante antes de añadir al carrito.")
        return redirect('tienda:home')

    producto = get_object_or_404(ProductoVariante, id=variante_id)
    form = CarritoAñadirProductoForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cantidad_anterior = carrito.carrito.get(str(producto.id), {}).get('cantidad', 0)
        carrito.añadir(producto=producto, cantidad=cd['cantidad'], sobreescribir=cd['sobreescribir'])
        
        # Verificar si se ajustó la cantidad por stock limitado
        if carrito.carrito[str(producto.id)]['cantidad'] < cantidad_anterior + cd['cantidad']:
            messages.warning(request, f"La cantidad se ajustó a {producto.stock} debido a disponibilidad limitada.")
    return redirect('carrito:carrito_detalle')


@require_POST
def carrito_eliminar(request, variante_id):
    carrito = Carrito(request)
    producto = get_object_or_404(ProductoVariante, id=variante_id)
    carrito.eliminar(producto)

        # Verificar si el carrito quedó vacío después de eliminar el producto
    if not carrito:
        messages.info(request, "Has eliminado todos los productos de tu carrito. Serás redirigido a la página de inicio.")
        return redirect('tienda:home')  # Redirigir a la página de inicio
    
    return redirect('carrito:carrito_detalle')


def carrito_detalle(request):
    carrito = Carrito(request)

    # Verificar si el carrito está vacío
    if not carrito:
        messages.warning(request, "Tu carrito está vacío. Por favor, añade productos antes de ver el detalle.")
        return redirect('tienda:home')

    # Recuperar el cupón desde la sesión
    coupon_id = request.session.get('coupon_id', None)
       
    for item in carrito:
        item['FormActualizarProducto'] = CarritoAñadirProductoForm(initial={
                            'cantidad': item.get('cantidad', 1),
                            'sobrescribir': True})

    coupon_apply_form = CouponApplyForm()
    r = Recomendador()
    carrito_productos = [item['producto'] for item in carrito]
    if carrito_productos:
        productos_recomendados = r.recomendar_productos_para(carrito_productos, max_results=4)
    else:
        productos_recomendados = []

    return render(request,
                  'carrito/detalle.html',
                  {'carrito': carrito,
                   'coupon_apply_form': coupon_apply_form,
                   'productos_recomendados': productos_recomendados})
