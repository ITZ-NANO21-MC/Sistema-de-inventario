from app import db
from app.models import Producto, ModeloTelefono, Usuario
from tests.factories import create_producto, create_modelo, create_usuario


def test_create_producto(db):
    producto = create_producto(db)
    assert producto.id is not None
    assert producto.nombre == 'Producto Test'
    assert producto.cantidad_stock == 10
    assert producto.stock_minimo == 5


def test_create_modelo(db):
    modelo = create_modelo(db)
    assert modelo.id is not None
    assert modelo.nombre == 'Modelo Test'
    assert modelo.marca == 'SAMSUNG'


def test_create_usuario(db):
    usuario = create_usuario(db)
    assert usuario.id is not None
    assert usuario.username == 'testuser'
    assert usuario.check_password('password123')
    assert usuario.rol == 'admin'


def test_create_producto_custom(db):
    producto = create_producto(
        db,
        nombre='Pantalla AMOLED',
        cantidad_stock=3,
        stock_minimo=5
    )
    assert producto.nombre == 'Pantalla AMOLED'
    assert producto.cantidad_stock == 3
    assert producto.cantidad_stock <= producto.stock_minimo
