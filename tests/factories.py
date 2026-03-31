from app.models import Producto, ModeloTelefono, Usuario


def create_producto(db, **kwargs):
    defaults = {
        'nombre': 'Producto Test',
        'descripcion': 'Descripcion de prueba',
        'categoria': 'pantalla',
        'marca': 'SAMSUNG',
        'cantidad_stock': 10,
        'stock_minimo': 5,
        'proveedor': 'Proveedor Test',
        'precio_mayor_bs': 100.00,
        'precio_mayor_usd': 10.00,
        'precio_detal_bs': 120.00,
        'precio_detal_usd': 12.00,
        'precio_tecnico_bs': 80.00,
        'precio_tecnico_usd': 8.00,
    }
    defaults.update(kwargs)
    producto = Producto(**defaults)
    db.session.add(producto)
    db.session.commit()
    return producto


def create_modelo(db, **kwargs):
    defaults = {
        'nombre': 'Modelo Test',
        'marca': 'SAMSUNG',
    }
    defaults.update(kwargs)
    modelo = ModeloTelefono(**defaults)
    db.session.add(modelo)
    db.session.commit()
    return modelo


def create_usuario(db, **kwargs):
    defaults = {
        'username': 'testuser',
        'rol': 'admin',
        'is_active': True,
    }
    defaults.update(kwargs)
    usuario = Usuario(**defaults)
    password = defaults.pop('password', 'password123')
    usuario.set_password(password)
    db.session.add(usuario)
    db.session.commit()
    return usuario
