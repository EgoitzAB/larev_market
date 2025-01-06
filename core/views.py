from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .mfa_backends import EmailMFADevice
from django.utils.timezone import now, timedelta
from django.views import generic
from allauth.account.models import EmailAddress
from .models import InfoTienda
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
    return render(request, 'core/perfil.html')