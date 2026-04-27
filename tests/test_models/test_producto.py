from decimal import Decimal
from app.models import Producto, ModeloTelefono


def test_create_producto_minimo(db):
    producto = Producto(
        nombre='Pantalla LCD',
        categoria='pantalla'
    )
    db.session.add(producto)
    db.session.commit()
    assert producto.id is not None
    assert producto.nombre == 'Pantalla LCD'
    assert producto.categoria == 'pantalla'
    assert producto.cantidad_stock == 0
    assert producto.stock_minimo == 5
    assert producto.marca is None
    assert producto.descripcion is None
    assert producto.proveedor is None


def test_create_producto_completo(db):
    producto = Producto(
        nombre='Pantalla AMOLED Samsung',
        descripcion='Pantalla de 6.5 pulgadas',
        categoria='pantalla',
        marca='SAMSUNG',
        cantidad_stock=50,
        stock_minimo=10,
        proveedor='Samsung Parts Co',
        precio_mayor_bs=Decimal('1000.00'),
        precio_mayor_usd=Decimal('100.00'),
        precio_detal_bs=Decimal('1200.00'),
        precio_detal_usd=Decimal('120.00'),
        precio_tecnico_bs=Decimal('800.00'),
        precio_tecnico_usd=Decimal('80.00')
    )
    db.session.add(producto)
    db.session.commit()
    assert producto.nombre == 'Pantalla AMOLED Samsung'
    assert producto.cantidad_stock == 50
    assert producto.stock_minimo == 10
    assert producto.precio_mayor_bs == Decimal('1000.00')
    assert producto.precio_tecnico_usd == Decimal('80.00')


def test_producto_precios_por_defecto(db):
    producto = Producto(nombre='Cable USB', categoria='cable')
    db.session.add(producto)
    db.session.commit()
    assert producto.precio_mayor_bs == Decimal('0.00')
    assert producto.precio_mayor_usd == Decimal('0.00')
    assert producto.precio_detal_bs == Decimal('0.00')
    assert producto.precio_detal_usd == Decimal('0.00')
    assert producto.precio_tecnico_bs == Decimal('0.00')
    assert producto.precio_tecnico_usd == Decimal('0.00')


def test_producto_stock_defecto(db):
    producto = Producto(nombre='Bateria', categoria='bateria')
    db.session.add(producto)
    db.session.commit()
    assert producto.cantidad_stock == 0
    assert producto.stock_minimo == 5


def test_producto_stock_bajo(db):
    producto = Producto(nombre='Cargador', categoria='cargador', cantidad_stock=2, stock_minimo=5)
    db.session.add(producto)
    db.session.commit()
    assert producto.cantidad_stock <= producto.stock_minimo


def test_producto_stock_adecuado(db):
    producto = Producto(nombre='Funda', categoria='funda', cantidad_stock=20, stock_minimo=5)
    db.session.add(producto)
    db.session.commit()
    assert producto.cantidad_stock > producto.stock_minimo


def test_producto_relacion_modelos(db):
    producto = Producto(nombre='Pantalla Galaxy', categoria='pantalla')
    modelo1 = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
    modelo2 = ModeloTelefono(nombre='Galaxy S22', marca='SAMSUNG')
    db.session.add_all([producto, modelo1, modelo2])
    db.session.flush()
    producto.modelos_compatibles.append(modelo1)
    producto.modelos_compatibles.append(modelo2)
    db.session.commit()
    assert len(producto.modelos_compatibles) == 2
    assert modelo1 in producto.modelos_compatibles
    assert modelo2 in producto.modelos_compatibles


def test_producto_repr(db):
    producto = Producto(nombre='Test Producto', categoria='otro')
    db.session.add(producto)
    db.session.commit()
    assert repr(producto) == '<Producto Test Producto>'


def test_producto_categorias(db):
    categorias = ['pantalla', 'bateria', 'funda', 'cable', 'cargador', 'otro']
    for cat in categorias:
        producto = Producto(nombre=f'Producto {cat}', categoria=cat)
        db.session.add(producto)
    db.session.commit()
    productos = Producto.query.all()
    assert len(productos) == 6
    categorias_db = {p.categoria for p in productos}
    assert categorias_db == set(categorias)


def test_producto_actualizar_stock(db):
    producto = Producto(nombre='Cable HDMI', categoria='cable', cantidad_stock=10)
    db.session.add(producto)
    db.session.commit()
    producto.cantidad_stock = 3
    db.session.commit()
    producto_actualizado = Producto.query.get(producto.id)
    assert producto_actualizado.cantidad_stock == 3


def test_producto_eliminar(db):
    producto = Producto(nombre='Eliminar', categoria='otro')
    db.session.add(producto)
    db.session.commit()
    producto_id = producto.id
    db.session.delete(producto)
    db.session.commit()
    assert Producto.query.get(producto_id) is None
