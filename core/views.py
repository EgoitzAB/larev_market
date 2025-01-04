from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .mfa_backends import EmailMFADevice
from django.utils.timezone import now, timedelta
from django.views import generic


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

    return render(request, 'core/mfa_verify.html')

class InfoTiendaView(generic.TemplateView):
    pass
    # """
    # A view that renders the personal page.

    # Attributes:
    #     model (Model): The model associated with the view.
    #     template_name (str): The name of the template to be rendered.

    # Methods:
    #     get_context_data(**kwargs): Retrieves the context data for the view.

    # """

    # model = Secciones
    # template_name = "core/personal.html"

    # def get_context_data(self, **kwargs):
    #     """
    #     Retrieves the context data for the view.

    #     Args:
    #         **kwargs: Additional keyword arguments.

    #     Returns:
    #         dict: The context data for the view.

    #     """
    #     context = super().get_context_data(**kwargs)
    #     context['secciones'] = Secciones.objects.filter(categoria='personal').order_by('indice')
    #     context['pdfs'] = PDF.objects.all()
    #     return context


class TerminosDeUsoView(generic.TemplateView):
    template_name = 'core/terminos_de_uso.html'


class PrivacidadView(generic.TemplateView):
    template_name = 'core/privacidad.html'