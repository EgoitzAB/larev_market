# CBD Marketplace

Un marketplace desarrollado en Django para la venta de productos CBD. Este proyecto incluye autenticación multi-factor (MFA) usando **django-allauth-mfa** e implementación personalizada de MFA por correo electrónico, asegurando un entorno seguro para los usuarios.


## 🚀 Características

- **Marketplace completo**: Catálogo de productos, carrito de compras y checkout.
- **Seguridad avanzada**: 
  - Autenticación multi-factor (MFA) integrada con `django-allauth-mfa`.
  - Implementación de MFA mediante correo electrónico.
- **Gestión de usuarios**:
  - Registro, inicio de sesión y recuperación de contraseñas.
  - Soporte para múltiples métodos de autenticación.
- **Diseño extensible**:
  - Estructura modular para facilitar la personalización y la adición de nuevas funcionalidades.

## 🛠️ Requisitos

- Python 3.8+
- Django 5.0+
- PostgreSQL (recomendado, pero soporta SQLite para desarrollo)

## ⚙️ Instalación

### 1. Clona el repositorio
```bash
git clone https://github.com/tuusuario/cbd-marketplace.git
cd cbd-marketplace
```

### 2. Configura el entorno virtual

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

### 3. Configura las variables de entorno

Crea un archivo .env en el directorio raíz basado en el ejemplo proporcionado:

cp .env.example .env

Edita el archivo .env para configurar tus credenciales, claves y la configuración de la base de datos.
### 4. Aplica las migraciones y carga datos iniciales

python manage.py migrate
python manage.py loaddata initial_data.json

### 5. Ejecuta el servidor de desarrollo

python manage.py runserver

Accede al proyecto en http://127.0.0.1:8000.
## 📦 Dependencias clave

    Django: Framework principal.
    django-allauth-mfa: Autenticación multi-factor.
    django-environ: Gestión de variables de entorno.

## 🛡️ Seguridad
Multi-Factor Authentication (MFA)

Este proyecto utiliza django-allauth-mfa para implementar autenticación multi-factor, con soporte para:

    MFA por correo electrónico: Los usuarios reciben un código único para autenticarse.
    Configuraciones avanzadas: Opciones para habilitar MFA obligatoria para ciertos usuarios o roles.

Recomendaciones de seguridad

    Usa HTTPS en producción.
    Protege tus claves y credenciales usando herramientas como AWS Secrets Manager o HashiCorp Vault.
    Habilita protección contra ataques como CSRF y XSS, ya configurados por Django por defecto.

## 🧑‍💻 Contribuir

¡Las contribuciones son bienvenidas! Sigue estos pasos:

    Haz un fork del repositorio.
    Crea una nueva rama:

git checkout -b feature/nueva-funcionalidad

Realiza tus cambios y realiza un commit:

git commit -m "Añadida nueva funcionalidad"

Haz un push a tu rama:

    git push origin feature/nueva-funcionalidad

    Abre un Pull Request en el repositorio original.

## 📝 Licencia

Este proyecto está licenciado bajo la **[GPLv3](LICENSE)**.

Consulta el archivo [LICENSE](LICENSE) para más detalles.

### 📄 Créditos

Desarrollado con ❤️ por [EgoitzAB].

Si tienes preguntas o sugerencias, contáctanos en [eabilleira1@protonmail.com].

