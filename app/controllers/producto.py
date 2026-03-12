from app.models import Producto
from app import db
from typing import Optional, List

class ProductoController:
    @staticmethod
    def obtener_todos() -> List[Producto]:
        return Producto.query.order_by(Producto.nombre).all()

    @staticmethod
    def obtener_por_id(id: int) -> Optional[Producto]:
        return Producto.query.get(id)

    @staticmethod
    def crear(data: dict) -> Producto:
        producto = Producto(
            nombre=data['nombre'],
            categoria=data['categoria'],
            cantidad_stock=data['cantidad_stock'],
            stock_minimo=data['stock_minimo'],
            proveedor=data.get('proveedor', '')
        )
        db.session.add(producto)
        db.session.commit()
        return producto

    @staticmethod
    def actualizar(id: int, data: dict) -> Optional[Producto]:
        producto = Producto.query.get(id)
        if not producto:
            return None
        producto.nombre = data['nombre']
        producto.categoria = data['categoria']
        producto.cantidad_stock = data['cantidad_stock']
        producto.stock_minimo = data['stock_minimo']
        producto.proveedor = data.get('proveedor', '')
        db.session.commit()
        return producto

    @staticmethod
    def eliminar(id: int) -> bool:
        producto = Producto.query.get(id)
        if not producto:
            return False
        db.session.delete(producto)
        db.session.commit()
        return True