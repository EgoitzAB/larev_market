from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from pagos.models import Orden
from weasyprint import HTML
from io import BytesIO


import logging

# Obtener el logger
logger = logging.getLogger(__name__)

@shared_task
def generar_enviar_factura(orden_id):
    try:
        logger.info(f"Iniciando la tarea para generar y enviar la factura de la orden ID {orden_id}")

        # Obtener la orden
        orden = Orden.objects.get(id=orden_id)
        logger.info(f"Orden encontrada: {orden} - Estado de la orden: {orden.estado}")

        # Verificar el estado de la orden y el pago
        pago = orden.pago
        logger.info(f"Pago encontrado para la orden ID {orden_id}: {pago} - Estado del pago: {pago.estado}")

        # Comprobar si el estado de la orden es 'completada' y el pago es 'exitoso'
        if orden.estado == 'completada':
            logger.info(f"Orden ID {orden_id} está completada y el pago es exitoso. Generando la factura.")

            # Preparar el contexto para la plantilla
            contexto = {'orden': orden}
            logger.info(f"Propiedades de la orden: {orden.id}, {orden.cliente.username}, {orden.total}, {orden.estado}")

            logger.info(f"Datos que se pasan a la plantilla: {contexto}")


            # Renderizar el HTML de la factura
            html_string = render_to_string('core/factura.html', contexto)
            logger.debug(f"HTML generado para la factura (primeros 500 caracteres): {html_string[:500]}")

            # Generar el PDF
            pdf_buffer = BytesIO()
            HTML(string=html_string).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)
            logger.info(f"PDF generado para la orden ID {orden_id}")

            # Enviar el correo con la factura adjunta
            email = EmailMessage(
                subject=f'Factura de Orden #{orden.id}',
                body='Adjuntamos su factura en PDF.',
                from_email=settings.EMAIL_HOST_USER,
                to=[orden.cliente.email],
            )
            email.attach(f'factura_{orden.id}.pdf', pdf_buffer.read(), 'application/pdf')
            email.send()
            logger.info(f"Factura enviada a {orden.cliente.email} para la orden ID {orden_id}")
            
            return f'Factura enviada para Orden #{orden.id}'
        else:
            logger.error(f"Orden ID {orden_id} no está completada o pago no exitoso. Estado de la orden: {orden.estado}, Estado del pago: {pago.estado}")
            return f'Orden no está completada o pago no exitoso. Orden ID: {orden_id}, Estado orden: {orden.estado}, Estado pago: {pago.estado}'

    except Orden.DoesNotExist:
        logger.error(f"Orden con ID {orden_id} no encontrada.")
        return f'Orden con ID {orden_id} no encontrada.'
    except Exception as e:
        logger.error(f"Error al generar la factura para la orden con ID {orden_id}: {str(e)}")
        return f'Error al generar la factura para la orden con ID {orden_id}: {str(e)}'

