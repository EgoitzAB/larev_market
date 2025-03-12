from __future__ import absolute_import, unicode_literals
from celery import Celery

import os

# Establecer la configuración de Django para Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "larev.settings")

app = Celery("larev")

# Cargar configuración desde settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks dentro de las aplicaciones registradas en Django
app.autodiscover_tasks()