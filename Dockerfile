# Usar Python como imagen base
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (libpq-dev es útil si usas PostgreSQL)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requerimientos
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear carpeta para archivos estáticos
RUN mkdir -p /app/staticfiles

# Colectar archivos estáticos (solo si es necesario en desarrollo, si no lo necesitas puedes omitirlo)
RUN python manage.py collectstatic --noinput

# Exponer el puerto del contenedor
EXPOSE 8000

# Especificar el comando para ejecutar Django en modo desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
