import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponseBadRequest

def validate_paygreen_signature(request):
    signature = request.headers.get('X-Paygreen-Signature')
    if not signature:
        return HttpResponseBadRequest("Missing signature header")

    # Si PayGreen manda "sha256=<hex>"
    if signature.startswith("sha256="):
        sig_hash = signature.split("=", 1)[1]
    else:
        sig_hash = signature

    # Calculamos el HMAC sobre el body completo
    computed_hmac = hmac.new(
        key=settings.PAYGREEN_HMAC_KEY.encode('utf-8'),
        msg=request.body,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Comparación en tiempo constante
    if not hmac.compare_digest(computed_hmac, sig_hash):
        return HttpResponseBadRequest("Invalid signature")

    # Si todo OK, devolvemos None para continuar el flujo
    return None
