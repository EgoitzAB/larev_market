from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Coupon
from .forms import CouponApplyForm
from carrito.carrito import Carrito

@require_POST
def coupon_apply(request):
    carrito = Carrito(request)  # Usamos la clase Carrito para acceder a la sesión
    form = CouponApplyForm(request.POST)

    if form.is_valid():
        code = form.cleaned_data['code']
        now = timezone.now()
        try:
            # Buscar el cupón en la base de datos
            coupon = Coupon.objects.get(code__iexact=code, fecha_inicio__lte=now, fecha_fin__gte=now, activo=True)
            
            # Aplicar el cupón usando el método de la clase Carrito
            carrito.apply_coupon(coupon.id)
            messages.success(request, f"¡Cupón '{coupon.code}' aplicado correctamente!")
        except Coupon.DoesNotExist:
            # Eliminar el cupón si no existe o no es válido
            carrito.remove_coupon()
            messages.error(request, "¡Cupón inválido o expirado!")
    
    return redirect('carrito:carrito_detalle')  # Redirige al detalle del carrito
