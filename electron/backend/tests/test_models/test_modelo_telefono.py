from app.models import ModeloTelefono, Producto


def test_create_modelo_completo(db):
    modelo = ModeloTelefono(nombre='Galaxy S23', marca='SAMSUNG')
    db.session.add(modelo)
    db.session.commit()
    assert modelo.id is not None
    assert modelo.nombre == 'Galaxy S23'
    assert modelo.marca == 'SAMSUNG'


def test_create_modelo_sin_marca(db):
    modelo = ModeloTelefono(nombre='iPhone 14')
    db.session.add(modelo)
    db.session.commit()
    assert modelo.nombre == 'iPhone 14'
    assert modelo.marca is None


def test_modelo_nombre_unico(db):
    modelo1 = ModeloTelefono(nombre='Redmi Note 12', marca='XIAOMI')
    modelo2 = ModeloTelefono(nombre='Redmi Note 12', marca='XIAOMI')
    db.session.add(modelo1)
    db.session.commit()
    db.session.add(modelo2)
    try:
        db.session.commit()
        assert False, 'Se esperaba IntegrityError por nombre duplicado'
    except Exception:
        db.session.rollback()


def test_modelo_repr(db):
    modelo = ModeloTelefono(nombre='Moto G53', marca='MOTOROLA')
    db.session.add(modelo)
    db.session.commit()
    assert repr(modelo) == '<Modelo Moto G53>'


def test_modelo_relacion_productos(db):
    modelo = ModeloTelefono(nombre='Galaxy A54', marca='SAMSUNG')
    producto1 = Producto(nombre='Pantalla A54', categoria='pantalla')
    producto2 = Producto(nombre='Funda A54', categoria='funda')
    db.session.add_all([modelo, producto1, producto2])
    db.session.flush()
    modelo.productos.append(producto1)
    modelo.productos.append(producto2)
    db.session.commit()
    assert len(modelo.productos) == 2
    assert producto1 in modelo.productos
    assert producto2 in modelo.productos


def test_modelo_actualizar(db):
    modelo = ModeloTelefono(nombre='Galaxy S20', marca='SAMSUNG')
    db.session.add(modelo)
    db.session.commit()
    modelo.nombre = 'Galaxy S20 FE'
    modelo.marca = 'Samsung Mobile'
    db.session.commit()
    modelo_actualizado = ModeloTelefono.query.get(modelo.id)
    assert modelo_actualizado.nombre == 'Galaxy S20 FE'
    assert modelo_actualizado.marca == 'Samsung Mobile'


def test_modelo_eliminar(db):
    modelo = ModeloTelefono(nombre='Eliminar Modelo', marca='OTROS')
    db.session.add(modelo)
    db.session.commit()
    modelo_id = modelo.id
    db.session.delete(modelo)
    db.session.commit()
    assert ModeloTelefono.query.get(modelo_id) is None


def test_modelo_distintas_marcas(db):
    marcas = ['SAMSUNG', 'XIAOMI', 'MOTOROLA', 'HUAWEI', 'IPHONE']
    for i, marca in enumerate(marcas):
        db.session.add(ModeloTelefono(nombre=f'Modelo {marca}', marca=marca))
    db.session.commit()
    modelos = ModeloTelefono.query.all()
    assert len(modelos) == 5
    marcas_db = {m.marca for m in modelos}
    assert marcas_db == set(marcas)
