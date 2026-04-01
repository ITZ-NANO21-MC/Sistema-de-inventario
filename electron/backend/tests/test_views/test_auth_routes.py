from app.models import Usuario


class TestLoginGet:
    def test_login_page_unauthenticated(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_redirect_authenticated(self, app, client):
        with app.app_context():
            user = Usuario(username='testuser', rol='admin')
            user.set_password('testpass123')
            from app import db
            db.session.add(user)
            db.session.commit()
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        response = client.get('/login')
        assert response.status_code == 302


class TestLoginPost:
    def test_login_valid_credentials(self, app, client):
        with app.app_context():
            user = Usuario(username='testuser', rol='admin')
            user.set_password('testpass123')
            from app import db
            db.session.add(user)
            db.session.commit()
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_invalid_password(self, app, client):
        with app.app_context():
            user = Usuario(username='testuser', rol='admin')
            user.set_password('testpass123')
            from app import db
            db.session.add(user)
            db.session.commit()
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_nonexistent_user(self, client):
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'anypass'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_empty_fields(self, client):
        response = client.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        assert response.status_code == 200


class TestLogout:
    def test_logout_redirects_to_login(self, app, client):
        with app.app_context():
            user = Usuario(username='testuser', rol='admin')
            user.set_password('testpass123')
            from app import db
            db.session.add(user)
            db.session.commit()
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
