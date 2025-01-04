import secrets
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django.db import models

class EmailMFADevice(models.Model):
    """
    Modelo que almacena los códigos enviados por correo electrónico.
    """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        """
        Genera un nuevo código MFA y lo envía al correo del usuario.
        """
        self.code = secrets.token_hex(3).upper()  # Código de 6 caracteres
        self.created_at = now()
        self.save()

        send_mail(
            subject='Tu código MFA',
            message=f'Tu código de inicio de sesión es: {self.code}',
            from_email='tu-email@example.com',
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_valid(self, code):
        """
        Verifica si el código ingresado es válido y no ha expirado.
        """
        return self.code == code and self.created_at >= now() - timedelta(minutes=10)  # Expira en 10 minutos

    class Meta:
        app_label = 'core'