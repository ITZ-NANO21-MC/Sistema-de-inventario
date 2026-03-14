from sqlalchemy.orm import joinedload
from app.models import Producto, ModeloTelefono
from app import db
from typing import Optional, List

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