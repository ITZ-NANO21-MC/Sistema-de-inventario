from sqlalchemy.orm import joinedload
from app.models import Producto, ModeloTelefono
from app import db
from typing import Optional, List
from flask import current_app


def verificar_stock_y_notificar(app):
    """Función que consulta todos los productos y verifica si alguno tiene
    un stock menor o igual al mínimo. Si los hay, envía un correo."""
    with app.app_context():
        productos_bajos = Producto.query.filter(Producto.cantidad_stock <= Producto.stock_minimo).all()
        
        if productos_bajos:
            app.logger.info(f"Se encontraron {len(productos_bajos)} productos con stock bajo. Enviando alerta...")
            from app.services.alertas import enviar_alerta_email
            enviar_alerta_email(app, productos_bajos)
        else:
            app.logger.info("Stock verificado: Todos los productos tienen niveles adecuados.")

class ProductoController:
    @staticmethod
    def obtener_todos() -> List[Producto]:
        return Producto.query.options(joinedload(Producto.modelos_compatibles)).order_by(Producto.nombre).all()

    @staticmethod
    def obtener_por_id(id: int) -> Optional[Producto]:
        return Producto.query.options(joinedload(Producto.modelos_compatibles)).filter(Producto.id == id).first()

    @staticmethod
    def crear(data: dict, modelos_ids: list = None) -> Producto:
        producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            categoria=data['categoria'],
            cantidad_stock=data['cantidad_stock'],
            stock_minimo=data['stock_minimo'],
            proveedor=data.get('proveedor', '')
        )
        if modelos_ids:
            modelos = ModeloTelefono.query.filter(ModeloTelefono.id.in_(modelos_ids)).all()
            producto.modelos_compatibles = modelos
        db.session.add(producto)
        db.session.commit()
        
        if producto.cantidad_stock <= producto.stock_minimo:
            verificar_stock_y_notificar(current_app._get_current_object())
        
        return producto

    @staticmethod
    def actualizar(id: int, data: dict, modelos_ids: list = None) -> Optional[Producto]:
        producto = Producto.query.get(id)
        if not producto:
            return None
        producto.nombre = data['nombre']
        producto.descripcion = data.get('descripcion', '')
        producto.categoria = data['categoria']
        producto.cantidad_stock = data['cantidad_stock']
        producto.stock_minimo = data['stock_minimo']
        producto.proveedor = data.get('proveedor', '')

        if modelos_ids is not None:
            print(f"[DEPURACIÓN] modelos_ids recibidos: {modelos_ids}")
            modelos = ModeloTelefono.query.filter(ModeloTelefono.id.in_(modelos_ids)).all()
            print(f"[DEPURACIÓN] modelos encontrados: {[m.nombre for m in modelos]}")
            producto.modelos_compatibles = modelos

        db.session.commit()
        print(f"[DEPURACIÓN] Producto {id} guardado. Modelos compatibles ahora: {[m.nombre for m in producto.modelos_compatibles]}")
        
        if producto.cantidad_stock <= producto.stock_minimo:
            verificar_stock_y_notificar(current_app._get_current_object())
        
        db.session.expire(producto)
        return producto

    @staticmethod
    def eliminar(id: int) -> bool:
        producto = Producto.query.get(id)
        if not producto:
            return False
        db.session.delete(producto)
        db.session.commit()
        return True