from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .mfa_backends import EmailMFADevice
from django.utils.timezone import now, timedelta
from django.urls import reverse
from django.views import generic
from allauth.account.models import EmailAddress
from .models import InfoTienda, Favorito
from tienda.models import ProductoVariante
from pagos.models import Orden
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from core.tasks import generar_enviar_factura

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
    # Obtener los favoritos del usuario
    favoritos = Favorito.objects.filter(usuario=request.user)
    # Obtener las órdenes no finalizadas (estado diferente a 'completada')
    ordenes_no_finalizadas = Orden.objects.filter(cliente=request.user).exclude(estado='completada')
    # Obtener el historial de compras (órdenes completadas)
    historial_compras = Orden.objects.filter(cliente=request.user, estado='completada')
    context = {
        'favoritos': favoritos,
        'ordenes_no_finalizadas': ordenes_no_finalizadas,
        'historial_compras': historial_compras,
    }
    return render(request, 'core/perfil.html', context)

@login_required(login_url='account_login')
def toggle_favorito(request):
    """
    Permite añadir o quitar un producto de favoritos con AJAX.
    Solo funciona si el usuario está autenticado.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    variante_id = request.POST.get("variante_id")
    if not variante_id:
        return JsonResponse({"error": "No se proporcionó una variante válida."}, status=400)

    variante = get_object_or_404(ProductoVariante, id=variante_id)

    favorito, created = Favorito.objects.get_or_create(usuario=request.user, producto_variante=variante)
  
    if not created:
        favorito.delete()
        messages.success(request, f"{variante.nombre} eliminado de tus favoritos.")
        return JsonResponse({"added": False})
    
    messages.success(request, f"{variante.nombre} añadido a tus favoritos.")
    return JsonResponse({"added": True})

@login_required
def guardar_favoritos(request):
    """
    Guarda los favoritos del usuario cuando se cierra sesión o el navegador.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        favoritos = data.get("favoritos", [])

        # Elimina los actuales favoritos del usuario
        Favorito.objects.filter(usuario=request.user).delete()

        # Guarda los nuevos favoritos
        for variante_id in favoritos:
            variante = get_object_or_404(ProductoVariante, id=variante_id)
            Favorito.objects.get_or_create(usuario=request.user, producto_variante=variante)

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Método no permitido."}, status=405)

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

def enviar_factura(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, pago__estado='exitoso')
    generar_enviar_factura.delay(orden.id)  # Llamada asíncrona con Celery
    return JsonResponse({'mensaje': 'Factura en proceso de envío.'})

@login_required
def descargar_factura(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, cliente=request.user)

    # Verificar que la orden está completada y el pago es exitoso
    if orden.estado != 'completada' or orden.pago.estado != 'exitoso':
        return HttpResponse("No puedes descargar la factura de una orden no completada.", status=400)

    # Renderizar la factura en HTML
    contexto = {'orden': orden}
    html_string = render_to_string('core/factura.html', contexto)

    # Generar PDF
    pdf_buffer = BytesIO()
    HTML(string=html_string).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    # Crear respuesta para la descarga
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{orden.id}.pdf"'
    return response