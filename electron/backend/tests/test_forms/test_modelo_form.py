from app.forms import ModeloForm


def test_modelo_form_valid(app):
    with app.test_request_context():
        form = ModeloForm(data={
            'nombre': 'Galaxy S23',
            'marca': 'SAMSUNG'
        })
        assert form.validate() is True


def test_modelo_form_valid_sin_marca(app):
    with app.test_request_context():
        form = ModeloForm(data={
            'nombre': 'Modelo generico'
        })
        assert form.validate() is True


def test_modelo_form_missing_nombre(app):
    with app.test_request_context():
        form = ModeloForm(data={
            'marca': 'SAMSUNG'
        })
        assert form.validate() is False
        assert 'nombre' in form.errors


def test_modelo_form_nombre_vacio(app):
    with app.test_request_context():
        form = ModeloForm(data={
            'nombre': '',
            'marca': 'SAMSUNG'
        })
        assert form.validate() is False
        assert 'nombre' in form.errors


def test_modelo_form_nombre_largo(app):
    with app.test_request_context():
        form = ModeloForm(data={
            'nombre': 'A' * 101,
            'marca': 'SAMSUNG'
        })
        assert form.validate() is False
        assert 'nombre' in form.errors


def test_modelo_form_nombre_maximo(app):
    with app.test_request_context():
        form = ModeloForm(data={
            'nombre': 'A' * 100,
            'marca': 'SAMSUNG'
        })
        assert form.validate() is True


def test_modelo_form_marcas_validas(app):
    marcas = ['', 'SAMSUNG', 'XIAOMI', 'MOTOROLA', 'HUAWEI', 'IPHONE', 'Otros']
    for marca in marcas:
        with app.test_request_context():
            form = ModeloForm(data={
                'nombre': 'Test',
                'marca': marca
            })
            assert form.validate() is True, f'Marca {marca} deberia ser valida'
