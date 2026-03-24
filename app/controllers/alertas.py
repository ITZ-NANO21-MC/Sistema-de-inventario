from app.models import Producto, ConfiguracionSistema
from app import db
from datetime import datetime


class AlertaController:
    @staticmethod
    def obtener_productos_bajos():
        return Producto.query.filter(
            Producto.cantidad_stock <= Producto.stock_minimo
        ).all()
    
    @staticmethod
    def obtener_productos_bajos_count():
        return Producto.query.filter(
            Producto.cantidad_stock <= Producto.stock_minimo
        ).count()
    
    @staticmethod
    def obtener_ultima_alerta_global():
        config = ConfiguracionSistema.query.filter_by(
            clave='ultima_alerta_global'
        ).first()
        if config and config.valor:
            try:
                # Python 3.12 fromisoformat maneja 'YYYY-MM-DD HH:MM:SS.mmmmmm'
                return datetime.fromisoformat(str(config.valor))
            except ValueError:
                pass
        return None
    
    @staticmethod
    def guardar_fecha_global():
        ahora = datetime.now()
        config = ConfiguracionSistema.query.filter_by(
            clave='ultima_alerta_global'
        ).first()
        if config:
            config.valor = ahora
        else:
            config = ConfiguracionSistema(
                clave='ultima_alerta_global',
                valor=ahora
            )
            db.session.add(config)
        db.session.commit()
    
    @staticmethod
    def guardar_fechas_productos(productos):
        ahora = datetime.now()
        for producto in productos:
            producto.ultima_notificacion = ahora
        db.session.commit()
