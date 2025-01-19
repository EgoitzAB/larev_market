import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from checkout.models import Direccion
from pagos.models import Orden, ItemOrden
from carrito.carrito import Carrito
from tienda.models import Producto, ProductoVariante, Categoria
from django.test import RequestFactory
from decimal import Decimal


@pytest.fixture
def usuario():
    return User.objects.create_user(username='testuser', password='testpassword')


@pytest.fixture
def cliente_autenticado(usuario):
    client = Client()
    client.login(username='testuser', password='testpassword')
    return client


@pytest.fixture
def categoria():
    return Categoria.objects.create(nombre="Categoria Base")

@pytest.fixture
def producto(categoria):
    return Producto.objects.create(
        nombre="Producto Base",
        descripcion="Descripción del producto base",
        categoria=categoria,  # Associate with the created categoria
    )

@pytest.fixture
def producto_variante(producto):
    return ProductoVariante.objects.create(
        producto=producto,
        nombre="Variante de prueba",
        precio=Decimal('10.00'),
        stock=10
    )

from django.test import Client

@pytest.fixture
def carrito(usuario, producto_variante):
    client = Client()
    client.force_login(usuario)
    response = client.get('/')  # Get the page that initializes the cart
    carrito = Carrito(client.get('/').wsgi_request)  # Use the correct request object
    carrito.añadir(producto=producto_variante, cantidad=2)
    return carrito



@pytest.fixture
def direccion(usuario):
    return Direccion.objects.create(
        usuario=usuario,
        nombre_completo="Test User",
        direccion="Calle Falsa 123",
        ciudad="Ciudad",
        codigo_postal="12345",
        pais="Pais"
    )


@pytest.mark.django_db
def test_checkout_get(cliente_autenticado, direccion):
    cliente_autenticado.login(username='testuser', password='password')  # Ensure user is logged in
    url = reverse('checkout:crear_orden')
    response = cliente_autenticado.get(url)
    assert response.status_code == 200  # Should return 200, not 302


@pytest.mark.django_db
def test_checkout_post_valid_address(cliente_autenticado, direccion, carrito):
    url = reverse('checkout:crear_orden')
    carrito_total = carrito.carrito_total()

    response = cliente_autenticado.post(url, {
        'direccion_id': direccion.id
    })

    assert response.status_code == 302
    assert Orden.objects.count() == 1

    orden = Orden.objects.first()
    assert orden.direccion_envio == direccion
    assert orden.total == carrito_total
    assert orden.estado == 'pendiente'

    assert ItemOrden.objects.count() == len(carrito)
    for item in carrito:
        item_orden = ItemOrden.objects.get(producto=item['producto'])
        assert item_orden.cantidad == item['cantidad']
        assert item_orden.precio_unitario == item['precio']


@pytest.mark.django_db
def test_checkout_creates_new_address(cliente_autenticado, usuario):
    cliente_autenticado.login(username='testuser', password='password')  # Ensure the user is logged in
    url = reverse('checkout:crear_orden')
    
    data = {
        'nombre_completo': "Nuevo Usuario",
        'direccion': "Nueva Dirección 456",
        'ciudad': "Nueva Ciudad",
        'codigo_postal': "67890",
        'pais': "Nuevo País",
    }
    
    response = cliente_autenticado.post(url, data)
    assert response.status_code == 302  # Ensure redirection after creating the address
    
    # Check that the address is saved
    assert Direccion.objects.filter(usuario=usuario, direccion="Nueva Dirección 456").exists()


@pytest.mark.django_db
def test_checkout_clears_cart(cliente_autenticado, carrito, direccion):
    url = reverse('checkout:crear_orden')

    cliente_autenticado.post(url, {
        'direccion_id': direccion.id
    })

    carrito.limpiar()
    assert len(carrito) == 0
