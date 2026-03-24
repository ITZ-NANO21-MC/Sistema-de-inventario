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
    def obtener_con_filtros(busqueda=None, categoria=None, precio_min=None, precio_max=None, 
                            precio_min_usd=None, precio_max_usd=None,
                            proveedor=None, stock_bajo=None, stock_minimo=None, stock_maximo=None) -> List[Producto]:
        query = Producto.query.options(joinedload(Producto.modelos_compatibles))
        
        # Filtro por nombre (búsqueda)
        if busqueda:
            query = query.filter(Producto.nombre.ilike(f'%{busqueda}%'))
        
        # Filtro por categoría
        if categoria:
            query = query.filter(Producto.categoria == categoria)
        
        # Filtro por precio mayor (Bs)
        if precio_min is not None:
            query = query.filter(Producto.precio_mayor_bs >= precio_min)
        if precio_max is not None:
            query = query.filter(Producto.precio_mayor_bs <= precio_max)
        
        # Filtro por precio mayor (USD)
        if precio_min_usd is not None:
            query = query.filter(Producto.precio_mayor_usd >= precio_min_usd)
        if precio_max_usd is not None:
            query = query.filter(Producto.precio_mayor_usd <= precio_max_usd)
        
        # Filtro por proveedor
        if proveedor:
            query = query.filter(Producto.proveedor.ilike(f'%{proveedor}%'))
        
        # Filtro por stock bajo/adecuado
        if stock_bajo == 'si':
            query = query.filter(Producto.cantidad_stock <= Producto.stock_minimo)
        elif stock_bajo == 'no':
            query = query.filter(Producto.cantidad_stock > Producto.stock_minimo)
        
        # Filtro por rango de stock
        if stock_minimo is not None:
            query = query.filter(Producto.cantidad_stock >= stock_minimo)
        if stock_maximo is not None:
            query = query.filter(Producto.cantidad_stock <= stock_maximo)
        
        return query.order_by(Producto.nombre).all()

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
            proveedor=data.get('proveedor', ''),
            precio_mayor_bs=data.get('precio_mayor_bs', 0),
            precio_mayor_usd=data.get('precio_mayor_usd', 0),
            precio_detal_bs=data.get('precio_detal_bs', 0),
            precio_detal_usd=data.get('precio_detal_usd', 0),
            precio_tecnico_bs=data.get('precio_tecnico_bs', 0),
            precio_tecnico_usd=data.get('precio_tecnico_usd', 0)
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
        producto.precio_mayor_bs = data.get('precio_mayor_bs', 0)
        producto.precio_mayor_usd = data.get('precio_mayor_usd', 0)
        producto.precio_detal_bs = data.get('precio_detal_bs', 0)
        producto.precio_detal_usd = data.get('precio_detal_usd', 0)
        producto.precio_tecnico_bs = data.get('precio_tecnico_bs', 0)
        producto.precio_tecnico_usd = data.get('precio_tecnico_usd', 0)

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