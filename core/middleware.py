from django.shortcuts import redirect

class EmailMFAMiddleware:
    """
    Middleware que redirige a la verificación MFA si no se ha completado.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.session.get('mfa_verified', False):
            if request.path != '/accounts/mfa/verify/':
                return redirect('verify_email_mfa')
        return self.get_response(request)
