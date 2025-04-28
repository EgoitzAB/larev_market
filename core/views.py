from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .mfa_backends import EmailMFADevice
from django.utils.timezone import now, timedelta
from django.urls import reverse
from django.views import generic
from allauth.account.models import EmailAddress
from .models import InfoTienda
from tienda.models import ProductoVariante
from pagos.models import Orden
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from core.tasks import generar_enviar_factura
from decimal import Decimal, ROUND_HALF_UP
from weasyprint import HTML
from io import BytesIO

import json


@login_required
def verify_email_mfa(request):
    """
    Vista para verificar el código MFA enviado por correo electrónico.
    """

    # Si ya está autenticado con MFA, no necesita verificar de nuevo.
    if request.session.get('mfa_verified', False):
        return redirect('tienda:home')  # Redirige al dashboard o página de inicio

    # Verificar si el correo electrónico está verificado
    email_address = EmailAddress.objects.filter(user=request.user, primary=True).first()
    if not email_address:
        # Si no hay correo principal, redirigir a configuración del perfil
        return redirect('account_email')  # Configura esta URL en tu proyecto

    if not email_address.verified:
        # Si no está verificado, redirige a la página de verificación de email
        if request.path != '/accounts/confirm-email/':
            return redirect('account_email_verification_sent')  # Ajusta esta URL

    # Obtener o crear el dispositivo MFA
    device, created = EmailMFADevice.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Verificar el código ingresado
        code = request.POST.get('code')
        if device.is_valid(code):
            # Marcar la sesión como verificada para MFA
            request.session['mfa_verified'] = True
            return redirect('tienda:home')  # Redirige al destino final
        else:
            return render(request, 'core/mfa_verify.html', {'error': 'Código inválido o expirado.'})

    # Generar y enviar un nuevo código si es necesario
    if not device.code or device.created_at < now() - timedelta(minutes=10):
        device.generate_code()

    return render(request, 'core/mfa_verify.html')


class InfoTiendaView(generic.TemplateView):
    template_name = "core/tienda_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info_tienda = get_object_or_404(InfoTienda, pk=1)  # Asumimos que hay solo un registro

        # Parsear ubicaciones desde JSON
        ubicaciones = json.loads(info_tienda.ubicaciones)

        # Agregar datos al contexto
        context.update({
            'nombre_tienda': info_tienda.nombre_tienda,
            'descripcion': info_tienda.descripcion,
            'mision': info_tienda.mision,
            'vision': info_tienda.vision,
            'ubicaciones': ubicaciones,
        })
        return context


class TerminosDeUsoView(generic.TemplateView):
    template_name = 'core/terminos_de_uso.html'


class PrivacidadView(generic.TemplateView):
    template_name = 'core/privacidad.html'


@login_required
def perfil(request):
    # Obtener las órdenes no finalizadas (estado diferente a 'completada')
    ordenes_no_finalizadas = Orden.objects.filter(cliente=request.user).exclude(estado='completada')
    # Obtener el historial de compras (órdenes completadas)
    historial_compras = Orden.objects.filter(cliente=request.user, estado='completada')
    context = {
        'ordenes_no_finalizadas': ordenes_no_finalizadas,
        'historial_compras': historial_compras,
    }
    return render(request, 'core/perfil.html', context)

@login_required
def detalle_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, cliente=request.user)

    # Lógica para continuar la compra
    if request.method == 'POST' and 'continuar_compra' in request.POST:
        if orden.estado in ['pendiente', 'procesando']:
            # Redirigir al proceso de pago
            return redirect('pagos:realizar_compra', orden_id=orden.id)
        else:
            # Mostrar un mensaje de error si la orden no puede continuarse
            messages.error(request, 'No se puede continuar con esta orden.')

    return render(request, 'core/detalle_orden.html', {'orden': orden})

@login_required
def enviar_factura(request, orden_id):
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        messages.error(request, "No se encontró esa orden.")
        return redirect('core:perfil')

    # Disparamos la tarea para generar y enviar la factura
    generar_enviar_factura.delay(orden.id)
    messages.success(request, f"Factura de la orden #{orden.id} en proceso de generación.")
    return redirect('core:perfil')

@login_required
def descargar_factura(request, orden_id):
    try:
        orden = Orden.objects.get(id=orden_id, cliente=request.user)
    except Orden.DoesNotExist:
        messages.error(request, "No se encontró esa orden.")
        return redirect('core:perfil')
    # Calcular IVA
    total = orden.get_total_cost()  # Este total ya INCLUYE IVA (21%)
    iva_rate = Decimal("0.21")

    # 1) Base imponible: separar el IVA
    divisor = (Decimal("1.00") + iva_rate)
    base_imponible = (total / divisor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # 2) IVA = total - base imponible
    iva = (total - base_imponible).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # 3) Total con IVA = total (sin cambios)
    total_con_iva = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    total_weight = sum(
        (item.producto.peso or Decimal("0")) * item.cantidad
        for item in orden.items.all()
    )
    # Redondear a 2 decimales si fuera decimal
    total_weight = total_weight.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Generar y descargar PDF
    html_string = render_to_string('core/factura.html', {
                                                        'orden': orden,
                                                        'base_imponible': base_imponible,
                                                        'iva': iva,
                                                        'total_con_iva': total_con_iva,
                                                        'total_weight': total_weight,  # en gramos
                                        })
    pdf_buffer = BytesIO()
    HTML(string=html_string).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{orden.id}.pdf"'
    return response