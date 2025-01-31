import os
from celery import Celery

# Configuración básica de Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'larev.settings')
celery_app = Celery('larev')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()
