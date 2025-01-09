from django.shortcuts import redirect
from django.urls import reverse

class VerificacionEdadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rutas que deben excluirse del middleware
        rutas_excluidas = [reverse('tienda:verificar_edad'), reverse('tienda:home')]
        
        # Verificar si el usuario ya confirmó su edad
        if not request.session.get('es_mayor_de_edad', False):
            # Si la ruta actual está en las rutas excluidas, permite continuar
            if request.path in rutas_excluidas:
                return self.get_response(request)
            # Si no, redirige a la página inicial para mostrar el modal
            return redirect('tienda:home')

        # Permite continuar si ya se verificó la edad
        response = self.get_response(request)
        return response