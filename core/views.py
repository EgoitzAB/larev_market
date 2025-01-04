from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .mfa_backends import EmailMFADevice
from django.utils.timezone import now, timedelta


@login_required
def verify_email_mfa(request):
    device, created = EmailMFADevice.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Verificar el código ingresado
        code = request.POST.get('code')
        if device.is_valid(code):
            request.session['mfa_verified'] = True
            return redirect('dashboard')  # Redirige al dashboard u otra página
        else:
            return render(request, 'mfa_verify.html', {'error': 'Código inválido o expirado.'})

    # Generar y enviar un nuevo código si es necesario
    if not device.code or device.created_at < now() - timedelta(minutes=10):
        device.generate_code()

    return render(request, 'mfa_verify.html')
