from app.models import ModeloTelefono


class TestListarModelos:
    def test_listar_autenticado(self, auth_client):
        response = auth_client.get('/modelos/', follow_redirects=True)
        assert response.status_code == 200

    def test_listar_no_autenticado(self, client):
        response = client.get('/modelos/', follow_redirects=True)
        assert response.status_code == 200

    def test_listar_con_modelos(self, auth_client, db):
        db.session.add_all([
            ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG'),
            ModeloTelefono(nombre='Redmi Note 12', marca='XIAOMI')
        ])
        db.session.commit()
        response = auth_client.get('/modelos/', follow_redirects=True)
        assert response.status_code == 200

    def test_listar_con_filtro(self, auth_client, db):
        db.session.add_all([
            ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG'),
            ModeloTelefono(nombre='Galaxy S22', marca='SAMSUNG'),
            ModeloTelefono(nombre='Redmi Note 12', marca='XIAOMI')
        ])
        db.session.commit()
        response = auth_client.get('/modelos/?busqueda=Galaxy', follow_redirects=True)
        assert response.status_code == 200


class TestCrearModelo:
    def test_crear_get(self, auth_client):
        response = auth_client.get('/modelos/crear', follow_redirects=True)
        assert response.status_code == 200

    def test_crear_post_valido(self, auth_client, db):
        response = auth_client.post('/modelos/crear', data={
            'nombre': 'Galaxy S24',
            'marca': 'SAMSUNG'
        }, follow_redirects=True)
        assert response.status_code == 200
        modelo = ModeloTelefono.query.filter_by(nombre='Galaxy S24').first()
        assert modelo is not None
        assert response.status_code == 200
        modelo = ModeloTelefono.query.filter_by(nombre='Galaxy S24').first()
        assert modelo is not None

    def test_crear_post_invalido(self, auth_client):
        response = auth_client.post('/modelos/crear', data={
            'nombre': '',
            'marca': 'SAMSUNG'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestEditarModelo:
    def test_editar_get(self, auth_client, db):
        modelo = ModeloTelefono(nombre='Galaxy S20', marca='SAMSUNG')
        db.session.add(modelo)
        db.session.commit()
        response = auth_client.get(f'/modelos/editar/{modelo.id}', follow_redirects=True)
        assert response.status_code == 200

    def test_editar_post_valido(self, auth_client, db):
        modelo = ModeloTelefono(nombre='Galaxy S20', marca='SAMSUNG')
        db.session.add(modelo)
        db.session.commit()
        response = auth_client.post(f'/modelos/editar/{modelo.id}', data={
            'nombre': 'Galaxy S20 FE',
            'marca': 'SAMSUNG'
        }, follow_redirects=True)
        assert response.status_code == 200
        modelo_actualizado = ModeloTelefono.query.get(modelo.id)
        assert modelo_actualizado.nombre == 'Galaxy S20 FE'


class TestEliminarModelo:
    def test_eliminar_valido(self, auth_client, db):
        modelo = ModeloTelefono(nombre='Eliminar', marca='OTROS')
        db.session.add(modelo)
        db.session.commit()
        response = auth_client.post(f'/modelos/eliminar/{modelo.id}', follow_redirects=True)
        assert response.status_code == 200
        assert ModeloTelefono.query.get(modelo.id) is None
