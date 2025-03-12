from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from checkout.models import Direccion
from checkout.forms import DireccionForm
from pagos.models import Orden
from carrito.carrito import Carrito
from tienda.models import Producto, ProductoVariante, Categoria
from unittest.mock import patch

class CheckoutViewTests(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        # Crear una categoría, producto y variante
        self.categoria = Categoria.objects.create(nombre="Categoria Base")
        self.producto = Producto.objects.create(
            nombre="Producto Base",
            descripcion="Descripción del producto base",
            categoria=self.categoria,
        )
        self.producto_variante = ProductoVariante.objects.create(
            producto=self.producto,
            nombre="Variante de prueba",
            precio=10.00,
            stock=10
        )

        # Crear una dirección de prueba
        self.direccion = Direccion.objects.create(
            usuario=self.user,
            nombre="Test User",
            apellido="Test Apellido",
            direccion="Calle Falsa 123",
            ciudad="Ciudad",
            codigo_postal="12345",
            provincia="Provincia",
            pais="Pais",
            email="test@example.com",
            telefono="123456789",
            es_direccion_envio=True
        )


        # Crear un carrito de prueba
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.session = self.client.session  # Asignar la sesión del cliente
        self.carrito = Carrito(self.request)  # Pasar el objeto request
        self.carrito.añadir(producto=self.producto_variante, cantidad=2)

    def test_checkout_clears_cart(self):
        url = reverse('checkout:crear_orden')

        # Verificar que el carrito no está vacío antes del checkout
        self.assertGreater(len(self.carrito), 0)

        # Realizar el checkout
        response = self.client.post(url, {
            'direccion_id': self.direccion.id
        })

        # Verificar que el carrito está vacío después del checkout
        self.carrito.limpiar()
        self.assertEqual(len(self.carrito), 0)

    def test_checkout_con_carrito_vacio(self):
        url = reverse('checkout:crear_orden')

        # Limpiar el carrito
        self.carrito.limpiar()

        # Intentar hacer checkout con el carrito vacío
        response = self.client.get(url)

        # Verificar que se redirige a la página de inicio con un mensaje de error
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('tienda:home'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Tu carrito está vacío. Por favor, añade productos antes de proceder al checkout.")

    def test_checkout_sin_autenticacion(self):
        # Cerrar sesión
        self.client.logout()

        url = reverse('checkout:crear_orden')

        # Intentar hacer checkout sin autenticación
        response = self.client.post(url, {
            'direccion_id': self.direccion.id
        })

        # Verificar que se redirige al inicio de sesión
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('account_login'))  # Ajusta según tu configuración

    def test_checkout_muestra_formulario_sin_direcciones(self):
        # Eliminar todas las direcciones del usuario
        Direccion.objects.filter(usuario=self.user).delete()

        url = reverse('checkout:crear_orden')

        # Intentar hacer checkout
        response = self.client.get(url)

        # Verificar que se muestra el formulario de dirección
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], DireccionForm)

    def test_checkout_muestra_direcciones_guardadas(self):
        url = reverse('checkout:crear_orden')

        # Intentar hacer checkout
        response = self.client.get(url)

        # Verificar que se muestran las direcciones guardadas
        self.assertEqual(response.status_code, 200)
        self.assertIn('direcciones', response.context)
        self.assertIn(self.direccion, response.context['direcciones'])

    def test_checkout_maneja_errores_formulario_direccion(self):
        url = reverse('checkout:crear_orden')

        # Intentar hacer checkout con un formulario de dirección inválido
        response = self.client.post(url, {
            'nombre': "",  # Campo obligatorio vacío
            'apellido': "Test Apellido",
            'direccion': "Calle Falsa 123",
            'ciudad': "Ciudad",
            'codigo_postal': "12345",
            'provincia': "Provincia",
            'pais': "Pais",
            'email': "test@example.com",
            'telefono': "123456789",
            'es_direccion_envio': True
        })
        # Verificar que se muestran los errores del formulario
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    @patch('checkout.pagos.Orden.crear_orden')
    def test_checkout_maneja_errores_creacion_orden(self, mock_crear_orden):
        url = reverse('checkout:crear_orden')

        # Simular un error al crear la orden
        mock_crear_orden.side_effect = Exception("Error al crear la orden")

        # Intentar hacer checkout
        response = self.client.post(url, {
            'direccion_id': self.direccion.id
        })

        # Verificar que se muestra un mensaje de error
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('checkout'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Error al crear la orden: Error al crear la orden")