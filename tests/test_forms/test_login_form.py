from app.forms import LoginForm


def test_login_form_valid_data(app):
    with app.test_request_context():
        form = LoginForm(data={
            'username': 'admin',
            'password': 'secret'
        })
        assert form.validate() is True


def test_login_form_empty_username(app):
    with app.test_request_context():
        form = LoginForm(data={
            'username': '',
            'password': 'secret'
        })
        assert form.validate() is False
        assert 'username' in form.errors


def test_login_form_empty_password(app):
    with app.test_request_context():
        form = LoginForm(data={
            'username': 'admin',
            'password': ''
        })
        assert form.validate() is False
        assert 'password' in form.errors


def test_login_form_empty_fields(app):
    with app.test_request_context():
        form = LoginForm(data={
            'username': '',
            'password': ''
        })
        assert form.validate() is False
        assert 'username' in form.errors
        assert 'password' in form.errors


def test_login_form_remember_me(app):
    with app.test_request_context():
        form = LoginForm(data={
            'username': 'admin',
            'password': 'secret',
            'remember_me': True
        })
        assert form.validate() is True
        assert form.remember_me.data is True


def test_login_form_no_remember_me(app):
    with app.test_request_context():
        form = LoginForm(data={
            'username': 'admin',
            'password': 'secret',
            'remember_me': False
        })
        assert form.validate() is True
        assert form.remember_me.data is False
