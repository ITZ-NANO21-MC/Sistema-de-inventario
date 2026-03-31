import pytest
from app import create_app, db as _db
from app.models import Producto, ModeloTelefono, Compatibilidad, ConfiguracionSistema, Usuario


class TestingConfig:
    TESTING = True
    SECRET_KEY = 'testing-secret-key-that-is-long-enough-for-validation'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_inventario.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SERVER = None
    JOB_ALERTA_STOCK_ACTIVO = False
    JOB_INFORME_MANANA_ACTIVO = False
    JOB_INFORME_TARDE_ACTIVO = False
    JOB_BACKUP_ACTIVO = False
    TASA_CAMBIO_USD_BS = 0.0


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in [_db.metadata.tables.get('compatibilidad'),
                      _db.metadata.tables.get('productos'),
                      _db.metadata.tables.get('modelos_telefono'),
                      _db.metadata.tables.get('configuracion_sistema'),
                      _db.metadata.tables.get('usuarios')]:
            if table is not None:
                try:
                    _db.session.execute(table.delete())
                except Exception:
                    pass
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_client(app):
    client = app.test_client()
    with app.app_context():
        user = Usuario(username='testuser', rol='admin')
        user.set_password('testpass123')
        _db.session.add(user)
        _db.session.commit()
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    return client
