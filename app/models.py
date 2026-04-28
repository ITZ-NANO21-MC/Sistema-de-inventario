from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)
    categoria = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=True)
    cantidad_stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    stock_requerido = db.Column(db.Integer, default=0)
    proveedor = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultima_notificacion = db.Column(db.DateTime, nullable=True)
    
    # Campos de precio
    precio_mayor_bs = db.Column(db.Numeric(10, 2), default=0.0)
    precio_mayor_usd = db.Column(db.Numeric(10, 2), default=0.0)
    precio_detal_bs = db.Column(db.Numeric(10, 2), default=0.0)
    precio_detal_usd = db.Column(db.Numeric(10, 2), default=0.0)
    precio_tecnico_bs = db.Column(db.Numeric(10, 2), default=0.0)
    precio_tecnico_usd = db.Column(db.Numeric(10, 2), default=0.0)

    # Relación muchos a muchos con modelos de teléfono
    modelos_compatibles = db.relationship('ModeloTelefono', secondary='compatibilidad',
                                          back_populates='productos')

    def __repr__(self):
        return f'<Producto {self.nombre}>'


class ModeloTelefono(db.Model):
    __tablename__ = 'modelos_telefono'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    marca = db.Column(db.String(50), nullable=True)

    productos = db.relationship('Producto', secondary='compatibilidad',
                                back_populates='modelos_compatibles')

    def __repr__(self):
        return f'<Modelo {self.nombre}>'


class Compatibilidad(db.Model):
    __tablename__ = 'compatibilidad'

    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelos_telefono.id'), primary_key=True)


class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuracion_sistema'

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<Usuario {self.username}>'