from app import db
from app.models import Producto


def test_app_config(app):
    assert app.config['TESTING'] is True
    assert 'test_inventario.db' in app.config['SQLALCHEMY_DATABASE_URI']
    assert app.config['WTF_CSRF_ENABLED'] is False


def test_db_connection(app):
    with app.app_context():
        db.create_all()
        count = db.session.query(Producto).count()
        assert count == 0
        db.drop_all()


def test_client_exists(client):
    assert client is not None
