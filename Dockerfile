# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de dependencias
COPY requirements.txt /app/

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libglib2.0-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copiar el código (si no está montado como volumen)
COPY . /app/

# Comando por defecto (esto debería ser ejecutado dentro del contenedor, pero el comando en docker-compose sobrescribirá esto)
CMD ["celery", "-A", "larev", "worker", "--loglevel=info"]
