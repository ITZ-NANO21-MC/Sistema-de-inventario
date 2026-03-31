from app.models import Producto, ModeloTelefono, Compatibilidad


def test_compatibilidad_crear_relacion(db):
    producto = Producto(nombre='Pantalla Galaxy', categoria='pantalla')
    modelo = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
    db.session.add_all([producto, modelo])
    db.session.flush()
    producto.modelos_compatibles.append(modelo)
    db.session.commit()
    compatibilidad = Compatibilidad.query.filter_by(
        producto_id=producto.id, modelo_id=modelo.id
    ).first()
    assert compatibilidad is not None
    assert compatibilidad.producto_id == producto.id
    assert compatibilidad.modelo_id == modelo.id


def test_compatibilidad_multiples_modelos(db):
    producto = Producto(nombre='Pantalla Universal', categoria='pantalla')
    modelo1 = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
    modelo2 = ModeloTelefono(nombre='Galaxy S22', marca='SAMSUNG')
    db.session.add_all([producto, modelo1, modelo2])
    db.session.flush()
    producto.modelos_compatibles = [modelo1, modelo2]
    db.session.commit()
    assert len(producto.modelos_compatibles) == 2
    compatibilidades = Compatibilidad.query.filter_by(
        producto_id=producto.id
    ).all()
    assert len(compatibilidades) == 2


def test_compatibilidad_multiples_productos(db):
    modelo = ModeloTelefono(nombre='Redmi Note 12', marca='XIAOMI')
    producto1 = Producto(nombre='Pantalla Redmi', categoria='pantalla')
    producto2 = Producto(nombre='Funda Redmi', categoria='funda')
    db.session.add_all([modelo, producto1, producto2])
    db.session.flush()
    modelo.productos = [producto1, producto2]
    db.session.commit()
    assert len(modelo.productos) == 2
    compatibilidades = Compatibilidad.query.filter_by(
        modelo_id=modelo.id
    ).all()
    assert len(compatibilidades) == 2


def test_compatibilidad_eliminar_producto(db):
    producto = Producto(nombre='Pantalla Test', categoria='pantalla')
    modelo = ModeloTelefono(nombre='Modelo Test', marca='SAMSUNG')
    db.session.add_all([producto, modelo])
    db.session.flush()
    producto.modelos_compatibles.append(modelo)
    db.session.commit()
    compatibilidad = Compatibilidad.query.filter_by(
        producto_id=producto.id, modelo_id=modelo.id
    ).first()
    assert compatibilidad is not None
    db.session.delete(producto)
    db.session.commit()
    compatibilidad = Compatibilidad.query.filter_by(
        producto_id=producto.id, modelo_id=modelo.id
    ).first()
    assert compatibilidad is None


def test_compatibilidad_eliminar_modelo(db):
    producto = Producto(nombre='Pantalla Test', categoria='pantalla')
    modelo = ModeloTelefono(nombre='Modelo Test', marca='SAMSUNG')
    db.session.add_all([producto, modelo])
    db.session.flush()
    producto.modelos_compatibles.append(modelo)
    db.session.commit()
    compatibilidad = Compatibilidad.query.filter_by(
        producto_id=producto.id, modelo_id=modelo.id
    ).first()
    assert compatibilidad is not None
    db.session.delete(modelo)
    db.session.commit()
    compatibilidad = Compatibilidad.query.filter_by(
        producto_id=producto.id, modelo_id=modelo.id
    ).first()
    assert compatibilidad is None


def test_compatibilidad_producto_sin_modelos(db):
    producto = Producto(nombre='Cable USB', categoria='cable')
    db.session.add(producto)
    db.session.commit()
    assert len(producto.modelos_compatibles) == 0
    compatibilidades = Compatibilidad.query.filter_by(
        producto_id=producto.id
    ).all()
    assert len(compatibilidades) == 0


def test_compatibilidad_modelo_sin_productos(db):
    modelo = ModeloTelefono(nombre='Modelo Aislado', marca='OTROS')
    db.session.add(modelo)
    db.session.commit()
    assert len(modelo.productos) == 0
    compatibilidades = Compatibilidad.query.filter_by(
        modelo_id=modelo.id
    ).all()
    assert len(compatibilidades) == 0
