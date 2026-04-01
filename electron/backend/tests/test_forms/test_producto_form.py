from app.forms import ProductoForm
from app.models import ModeloTelefono


def test_producto_form_valid_minimal(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Pantalla LCD',
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        assert form.validate() is True


def test_producto_form_valid_complete(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Pantalla AMOLED Samsung',
            'descripcion': 'Pantalla de 6.5 pulgadas',
            'categoria': 'pantalla',
            'marca': 'SAMSUNG',
            'cantidad_stock': 50,
            'stock_minimo': 10,
            'proveedor': 'Samsung Parts',
            'precio_mayor_bs': 1000.00,
            'precio_mayor_usd': 100.00,
            'precio_detal_bs': 1200.00,
            'precio_detal_usd': 120.00,
            'precio_tecnico_bs': 800.00,
            'precio_tecnico_usd': 80.00
        })
        assert form.validate() is True


def test_producto_form_missing_nombre(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        assert form.validate() is False
        assert 'nombre' in form.errors


def test_producto_form_missing_categoria(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        assert form.validate() is False
        assert 'categoria' in form.errors


def test_producto_form_missing_cantidad_stock(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'pantalla',
            'stock_minimo': 5
        })
        assert form.validate() is False
        assert 'cantidad_stock' in form.errors


def test_producto_form_missing_stock_minimo(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'pantalla',
            'cantidad_stock': 10
        })
        assert form.validate() is False
        assert 'stock_minimo' in form.errors


def test_producto_form_stock_negativo(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'pantalla',
            'cantidad_stock': -1,
            'stock_minimo': 5
        })
        assert form.validate() is False
        assert 'cantidad_stock' in form.errors


def test_producto_form_stock_minimo_cero(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 0
        })
        assert form.validate() is False
        assert 'stock_minimo' in form.errors


def test_producto_form_nombre_largo(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'A' * 101,
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        assert form.validate() is False
        assert 'nombre' in form.errors


def test_producto_form_nombre_maximo(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'A' * 100,
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        assert form.validate() is True


def test_producto_form_descripcion_larga(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'descripcion': 'B' * 201,
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        form.validate()
        assert len(form.descripcion.data) <= 200 or 'descripcion' not in form.errors


def test_producto_form_proveedor_largo(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'proveedor': 'C' * 101,
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        form.validate()
        assert len(form.proveedor.data) <= 100 or 'proveedor' not in form.errors


def test_producto_form_categorias_validas(app, db):
    categorias = ['pantalla', 'bateria', 'funda', 'cable', 'cargador', 'otro']
    for cat in categorias:
        with app.test_request_context():
            form = ProductoForm(data={
                'nombre': f'Test {cat}',
                'categoria': cat,
                'cantidad_stock': 10,
                'stock_minimo': 5
            })
            assert form.validate() is True, f'Categoria {cat} deberia ser valida'


def test_producto_form_categoria_invalida(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'invalida',
            'cantidad_stock': 10,
            'stock_minimo': 5
        })
        assert form.validate() is False
        assert 'categoria' in form.errors


def test_producto_form_precios_validos(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5,
            'precio_mayor_bs': 100.50,
            'precio_mayor_usd': 10.00,
            'precio_detal_bs': 120.00,
            'precio_detal_usd': 12.00,
            'precio_tecnico_bs': 80.00,
            'precio_tecnico_usd': 8.00
        })
        assert form.validate() is True


def test_producto_form_precios_cero(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5,
            'precio_mayor_bs': 0,
            'precio_mayor_usd': 0
        })
        assert form.validate() is True


def test_producto_form_stock_cero_invalido(app, db):
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Test',
            'categoria': 'pantalla',
            'cantidad_stock': 0,
            'stock_minimo': 5
        })
        assert form.validate() is False
        assert 'cantidad_stock' in form.errors


def test_producto_form_marcas_validas(app, db):
    marcas = ['', 'SAMSUNG', 'XIAOMI', 'MOTOROLA', 'HUAWEI', 'IPHONE', 'Otros']
    for marca in marcas:
        with app.test_request_context():
            form = ProductoForm(data={
                'nombre': 'Test',
                'categoria': 'pantalla',
                'marca': marca,
                'cantidad_stock': 10,
                'stock_minimo': 5
            })
            assert form.validate() is True, f'Marca {marca} deberia ser valida'


def test_producto_form_modelos_compatibles(app, db):
    m1 = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
    m2 = ModeloTelefono(nombre='Galaxy S22', marca='SAMSUNG')
    db.session.add_all([m1, m2])
    db.session.commit()
    with app.test_request_context():
        form = ProductoForm(data={
            'nombre': 'Pantalla Galaxy',
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5,
            'modelos_compatibles': [m1.id, m2.id]
        })
        assert form.validate() is True
