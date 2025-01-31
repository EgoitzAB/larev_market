from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction

from weasyprint import HTML
from io import BytesIO
from pagos.models import Orden

@shared_task
def generar_enviar_factura(orden_id):
    try:
        orden = Orden.objects.get(id=orden_id, pago__estado='completada')
        contexto = {'orden': orden}
        html_string = render_to_string('factura.html', contexto)
        pdf_buffer = BytesIO()
        HTML(string=html_string).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        
        # Envío del correo con la factura adjunta
        email = EmailMessage(
            subject=f'Factura de Orden #{orden.id}',
            body='Adjuntamos su factura en PDF.',
            from_email= settings.EMAIL_HOST_USER,
            to=[orden.cliente.email],
        )
        email.attach(f'factura_{orden.id}.pdf', pdf_buffer.read(), 'application/pdf')
        email.send()
        
        return f'Factura enviada para Orden #{orden.id}'
    except Orden.DoesNotExist:
        return 'Orden no encontrada o no pagada.'

@shared_task
def liberar_stock_en_10_minutos(orden_id):
    """Verifica si la orden sigue pendiente después de 10 minutos y libera stock"""
    try:
        orden = Orden.objects.get(id=orden_id)
        if orden.estado == "pendiente":  # Si no se pagó, liberar stock
            with transaction.atomic():
                for item in orden.items.all():
                    item.producto.stock += item.cantidad
                    item.producto.save()

            # No eliminar la orden, solo cambiar el estado
            orden.estado = "fallida"
            orden.save()

            # También actualizar el estado del pago
            pago = orden.pago
            if pago:
                pago.estado = "fallido"
                pago.save()

    except Orden.DoesNotExist:
        pass

