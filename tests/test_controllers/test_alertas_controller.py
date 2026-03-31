from datetime import datetime
from app.controllers.alertas import AlertaController
from app.models import Producto, ConfiguracionSistema


class TestObtenerProductosBajos:
    def test_productos_bajos_con_resultados(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', cantidad_stock=2, stock_minimo=5),
            Producto(nombre='P2', categoria='funda', cantidad_stock=1, stock_minimo=3),
            Producto(nombre='P3', categoria='cable', cantidad_stock=20, stock_minimo=5)
        ])
        db.session.commit()
        productos = AlertaController.obtener_productos_bajos()
        assert len(productos) == 2
        assert all(p.cantidad_stock <= p.stock_minimo for p in productos)

    def test_productos_bajos_sin_resultados(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', cantidad_stock=20, stock_minimo=5),
            Producto(nombre='P2', categoria='funda', cantidad_stock=15, stock_minimo=3)
        ])
        db.session.commit()
        productos = AlertaController.obtener_productos_bajos()
        assert len(productos) == 0

    def test_productos_bajos_stock_igual_minimo(self, db):
        db.session.add(Producto(nombre='P1', categoria='otro', cantidad_stock=5, stock_minimo=5))
        db.session.commit()
        productos = AlertaController.obtener_productos_bajos()
        assert len(productos) == 1


class TestObtenerProductosBajosCount:
    def test_count_con_productos_bajos(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', cantidad_stock=2, stock_minimo=5),
            Producto(nombre='P2', categoria='funda', cantidad_stock=1, stock_minimo=3),
            Producto(nombre='P3', categoria='cable', cantidad_stock=20, stock_minimo=5)
        ])
        db.session.commit()
        count = AlertaController.obtener_productos_bajos_count()
        assert count == 2

    def test_count_sin_productos_bajos(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', cantidad_stock=20, stock_minimo=5)
        ])
        db.session.commit()
        count = AlertaController.obtener_productos_bajos_count()
        assert count == 0


class TestObtenerUltimaAlertaGlobal:
    def test_con_alerta_existente(self, db):
        fecha = '2024-01-15 08:30:00'
        db.session.add(ConfiguracionSistema(clave='ultima_alerta_global', valor=fecha))
        db.session.commit()
        resultado = AlertaController.obtener_ultima_alerta_global()
        assert resultado is not None
        assert resultado.year == 2024
        assert resultado.month == 1
        assert resultado.day == 15

    def test_sin_alerta_existente(self, db):
        resultado = AlertaController.obtener_ultima_alerta_global()
        assert resultado is None

    def test_alerta_con_formato_invalido(self, db):
        db.session.add(ConfiguracionSistema(clave='ultima_alerta_global', valor='formato_invalido'))
        db.session.commit()
        resultado = AlertaController.obtener_ultima_alerta_global()
        assert resultado is None

    def test_alerta_con_valor_nulo(self, db):
        db.session.add(ConfiguracionSistema(clave='ultima_alerta_global'))
        db.session.commit()
        resultado = AlertaController.obtener_ultima_alerta_global()
        assert resultado is None


class TestGuardarFechaGlobal:
    def test_guardar_nueva(self, db):
        AlertaController.guardar_fecha_global()
        config = ConfiguracionSistema.query.filter_by(
            clave='ultima_alerta_global'
        ).first()
        assert config is not None
        assert config.valor is not None

    def test_guardar_actualizar_existente(self, db):
        db.session.add(ConfiguracionSistema(
            clave='ultima_alerta_global',
            valor='2020-01-01 00:00:00'
        ))
        db.session.commit()
        AlertaController.guardar_fecha_global()
        config = ConfiguracionSistema.query.filter_by(
            clave='ultima_alerta_global'
        ).first()
        valor = datetime.fromisoformat(str(config.valor))
        assert valor.year == datetime.now().year


class TestGuardarFechasProductos:
    def test_guardar_fechas_multiples(self, db):
        productos = [
            Producto(nombre='P1', categoria='otro', cantidad_stock=10),
            Producto(nombre='P2', categoria='otro', cantidad_stock=10)
        ]
        db.session.add_all(productos)
        db.session.commit()
        AlertaController.guardar_fechas_productos(productos)
        for p in productos:
            assert p.ultima_notificacion is not None
            assert isinstance(p.ultima_notificacion, datetime)

    def test_guardar_fechas_lista_vacia(self, db):
        AlertaController.guardar_fechas_productos([])
