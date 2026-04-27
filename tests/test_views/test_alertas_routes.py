from unittest.mock import patch
from app.models import Producto


class TestListarAlertas:
    def test_listar_autenticado(self, auth_client):
        response = auth_client.get('/alertas', follow_redirects=True)
        assert response.status_code == 200

    def test_listar_no_autenticado(self, client):
        response = client.get('/alertas', follow_redirects=True)
        assert response.status_code == 200

    def test_listar_con_productos_bajos(self, auth_client, db):
        db.session.add(Producto(nombre='Bajo', categoria='otro', cantidad_stock=1, stock_minimo=5))
        db.session.commit()
        response = auth_client.get('/alertas', follow_redirects=True)
        assert response.status_code == 200


class TestEnviarAlerta:
    def test_enviar_alerta_autenticado(self, auth_client, db):
        db.session.add(Producto(nombre='Bajo', categoria='otro', cantidad_stock=1, stock_minimo=5))
        db.session.commit()
        with patch('app.services.alertas.verificar_stock_y_notificar'):
            response = auth_client.post('/alertas/enviar', follow_redirects=True)
            assert response.status_code == 200

    def test_enviar_alerta_no_autenticado(self, client):
        response = client.post('/alertas/enviar', follow_redirects=True)
        assert response.status_code == 200
