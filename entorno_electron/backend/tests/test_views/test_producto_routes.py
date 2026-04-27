from decimal import Decimal
from unittest.mock import patch
from app.models import Producto, ModeloTelefono


class TestListarProductos:
    def test_listar_autenticado(self, auth_client):
        response = auth_client.get('/productos/', follow_redirects=True)
        assert response.status_code == 200

    def test_listar_no_autenticado(self, client):
        response = client.get('/productos/', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'usuario' in response.data.lower()

    def test_listar_con_filtro(self, auth_client, db):
        db.session.add_all([
            Producto(nombre='Pantalla Samsung', categoria='pantalla'),
            Producto(nombre='Funda Xiaomi', categoria='funda')
        ])
        db.session.commit()
        response = auth_client.get('/productos/?busqueda=Samsung', follow_redirects=True)
        assert response.status_code == 200


class TestCrearProducto:
    def test_crear_get(self, auth_client):
        response = auth_client.get('/productos/crear', follow_redirects=True)
        assert response.status_code == 200

    def test_crear_post_valido(self, auth_client, db):
        response = auth_client.post('/productos/crear', data={
            'nombre': 'Nuevo Producto',
            'categoria': 'otro',
            'cantidad_stock': 10,
            'stock_minimo': 5
        }, follow_redirects=True)
        assert response.status_code == 200
        producto = Producto.query.filter_by(nombre='Nuevo Producto').first()
        assert producto is not None

    def test_crear_post_invalido(self, auth_client):
        response = auth_client.post('/productos/crear', data={
            'nombre': '',
            'categoria': '',
            'cantidad_stock': -1,
            'stock_minimo': 0
        }, follow_redirects=True)
        assert response.status_code == 200


class TestEditarProducto:
    def test_editar_get(self, auth_client, db):
        producto = Producto(nombre='Editar Test', categoria='otro', cantidad_stock=10, stock_minimo=5)
        db.session.add(producto)
        db.session.commit()
        response = auth_client.get(f'/productos/editar/{producto.id}', follow_redirects=True)
        assert response.status_code == 200

    def test_editar_no_existente(self, auth_client):
        response = auth_client.get('/productos/editar/999', follow_redirects=True)
        assert response.status_code == 200

    def test_editar_post_valido(self, auth_client, db):
        producto = Producto(nombre='Viejo', categoria='otro', cantidad_stock=10, stock_minimo=5)
        db.session.add(producto)
        db.session.commit()
        response = auth_client.post(f'/productos/editar/{producto.id}', data={
            'nombre': 'Nuevo Nombre',
            'categoria': 'otro',
            'cantidad_stock': 20,
            'stock_minimo': 10
        }, follow_redirects=True)
        assert response.status_code == 200
        producto_actualizado = Producto.query.get(producto.id)
        assert producto_actualizado.nombre == 'Nuevo Nombre'


class TestEliminarProducto:
    def test_eliminar_valido(self, auth_client, db):
        producto = Producto(nombre='Eliminar Test', categoria='otro')
        db.session.add(producto)
        db.session.commit()
        response = auth_client.post(f'/productos/eliminar/{producto.id}', follow_redirects=True)
        assert response.status_code == 200
        assert Producto.query.get(producto.id) is None


class TestActualizarStock:
    def test_actualizar_stock_valido(self, auth_client, db):
        producto = Producto(nombre='Stock Test', categoria='otro', cantidad_stock=10)
        db.session.add(producto)
        db.session.commit()
        response = auth_client.post(f'/productos/actualizar-stock/{producto.id}', data={
            'nuevo_stock': 25
        }, follow_redirects=True)
        assert response.status_code == 200
        producto_actualizado = Producto.query.get(producto.id)
        assert producto_actualizado.cantidad_stock == 25

    def test_actualizar_stock_invalido(self, auth_client, db):
        producto = Producto(nombre='Stock Test', categoria='otro', cantidad_stock=10)
        db.session.add(producto)
        db.session.commit()
        response = auth_client.post(f'/productos/actualizar-stock/{producto.id}', data={
            'nuevo_stock': -5
        }, follow_redirects=True)
        assert response.status_code == 200


class TestEnviarAlertaManual:
    def test_enviar_alerta(self, auth_client):
        with patch('app.views.producto_routes.verificar_stock_y_notificar'):
            response = auth_client.get('/productos/enviar-alerta-manual', follow_redirects=True)
            assert response.status_code == 200


class TestEnviarInformeManual:
    def test_enviar_informe(self, auth_client):
        with patch('app.views.producto_routes.generar_informe_general'):
            response = auth_client.get('/productos/enviar-informe-manual', follow_redirects=True)
            assert response.status_code == 200


class TestExportarExcel:
    def test_exportar(self, auth_client, db):
        db.session.add(Producto(nombre='Export Test', categoria='otro', cantidad_stock=10))
        db.session.commit()
        response = auth_client.get('/productos/exportar-excel', follow_redirects=True)
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
