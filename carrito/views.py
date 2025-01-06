from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from tienda.models import Producto
#from coupons.forms import CouponApplyForm
from tienda.recomendador import Recomendador
from .carrito import Carrito
from .forms import CarritoAñadirProductoForm


@require_POST
def carrito_añadir(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    form = CarritoAñadirProductoForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        carrito.añadir(product=producto,
                cantidad=cd['cantidad'],
                sobreescribir=cd['sobreescribir'])
    return redirect('carrito:carrito_detalle')


@require_POST
def carrito_eliminar(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.eliminar(producto)
    return redirect('carrito:carrito_detalle')


def carrito_detalle(request):
    carrito = Carrito(request)
    for item in carrito:
        item['FormActualizarProducto'] = CarritoAñadirProductoForm(initial={
                            'cantidad': item['cantidad'],
                            'sobrescribir': True})
#    coupon_apply_form = CouponApplyForm()
    r = Recomendador()
    carrito_productos = [item['producto'] for item in carrito]
    if(carrito_productos):
        productos_recomendados = r.recomendar_productos_para(carrito_productos,
                                                    max_results=4)
    else:
        productos_recomendados = []

    return render(request,
                'carrito/detalle.html',
                {'carrito': carrito,
                #'coupon_apply_form': coupon_apply_form,
                'productos_recomendados': productos_recomendados})
