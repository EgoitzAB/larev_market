# Usar Python como imagen base
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y mod_wsgi
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libglib2.0-dev \
    apache2 \
    apache2-dev \
    libapache2-mod-wsgi-py3 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requerimientos
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear carpeta para archivos estáticos
RUN mkdir -p /app/staticfiles

# Colectar archivos estáticos
RUN python manage.py collectstatic --noinput

# Variables de entorno para Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=larev.settings

# Exponer el puerto del contenedor
EXPOSE 80

# Especificar el comando para ejecutar Apache en modo producción
CMD ["apache2ctl", "-D", "FOREGROUND"]
