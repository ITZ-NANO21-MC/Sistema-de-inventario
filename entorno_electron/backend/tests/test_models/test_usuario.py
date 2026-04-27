from app.models import Usuario


def test_create_usuario(db):
    usuario = Usuario(username='admin', rol='admin')
    usuario.set_password('securepass123')
    db.session.add(usuario)
    db.session.commit()
    assert usuario.id is not None
    assert usuario.username == 'admin'
    assert usuario.rol == 'admin'
    assert usuario.is_active is True


def test_usuario_check_password_correcta(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('mypassword')
    db.session.add(usuario)
    db.session.commit()
    assert usuario.check_password('mypassword') is True


def test_usuario_check_password_incorrecta(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('mypassword')
    db.session.add(usuario)
    db.session.commit()
    assert usuario.check_password('wrongpassword') is False


def test_usuario_password_hashed(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('mypassword')
    db.session.add(usuario)
    db.session.commit()
    assert usuario.password_hash != 'mypassword'
    assert len(usuario.password_hash) > 20


def test_usuario_username_unico(db):
    usuario1 = Usuario(username='admin')
    usuario1.set_password('pass1')
    usuario2 = Usuario(username='admin')
    usuario2.set_password('pass2')
    db.session.add(usuario1)
    db.session.commit()
    db.session.add(usuario2)
    try:
        db.session.commit()
        assert False, 'Se esperaba IntegrityError por username duplicado'
    except Exception:
        db.session.rollback()


def test_usuario_rol_defecto(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    assert usuario.rol == 'admin'


def test_usuario_is_active_defecto(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    assert usuario.is_active is True


def test_usuario_desactivar(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    usuario.is_active = False
    db.session.commit()
    usuario_actualizado = Usuario.query.filter_by(username='testuser').first()
    assert usuario_actualizado.is_active is False


def test_usuario_cambiar_rol(db):
    usuario = Usuario(username='testuser', rol='admin')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    usuario.rol = 'viewer'
    db.session.commit()
    usuario_actualizado = Usuario.query.filter_by(username='testuser').first()
    assert usuario_actualizado.rol == 'viewer'


def test_usuario_repr(db):
    usuario = Usuario(username='admin')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    assert repr(usuario) == '<Usuario admin>'


def test_usuario_user_mixin_attributes(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    assert hasattr(usuario, 'is_authenticated')
    assert hasattr(usuario, 'is_active')
    assert hasattr(usuario, 'is_anonymous')
    assert hasattr(usuario, 'get_id')
    assert usuario.is_authenticated is True
    assert usuario.is_anonymous is False


def test_usuario_get_id(db):
    usuario = Usuario(username='testuser')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    assert usuario.get_id() == str(usuario.id)


def test_usuario_eliminar(db):
    usuario = Usuario(username='eliminar')
    usuario.set_password('pass')
    db.session.add(usuario)
    db.session.commit()
    usuario_id = usuario.id
    db.session.delete(usuario)
    db.session.commit()
    assert Usuario.query.get(usuario_id) is None
