from decimal import Decimal
from app.controllers.producto import ProductoController
from app.models import Producto, ModeloTelefono


class TestObtenerTodos:
    def test_obtener_todos_vacio(self, db):
        productos = ProductoController.obtener_todos()
        assert productos == []

    def test_obtener_todos_ordenados(self, db):
        p1 = Producto(nombre='Zebra', categoria='otro')
        p2 = Producto(nombre='Alfa', categoria='otro')
        p3 = Producto(nombre='Media', categoria='otro')
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        productos = ProductoController.obtener_todos()
        assert len(productos) == 3
        assert productos[0].nombre == 'Alfa'
        assert productos[1].nombre == 'Media'
        assert productos[2].nombre == 'Zebra'

    def test_obtener_todos_con_modelos(self, db):
        modelo = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
        db.session.add(modelo)
        db.session.flush()
        producto = Producto(nombre='Pantalla', categoria='pantalla')
        producto.modelos_compatibles.append(modelo)
        db.session.add(producto)
        db.session.commit()
        productos = ProductoController.obtener_todos()
        assert len(productos) == 1
        assert len(productos[0].modelos_compatibles) == 1


class TestObtenerConFiltros:
    def test_sin_filtros(self, db):
        db.session.add_all([
            Producto(nombre='A', categoria='pantalla'),
            Producto(nombre='B', categoria='funda')
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros()
        assert len(productos) == 2

    def test_filtro_busqueda(self, db):
        db.session.add_all([
            Producto(nombre='Pantalla Samsung', categoria='pantalla'),
            Producto(nombre='Pantalla Xiaomi', categoria='pantalla'),
            Producto(nombre='Funda', categoria='funda')
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(busqueda='Samsung')
        assert len(productos) == 1
        assert productos[0].nombre == 'Pantalla Samsung'

    def test_filtro_categoria(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla'),
            Producto(nombre='F1', categoria='funda'),
            Producto(nombre='C1', categoria='cable')
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(categoria='pantalla')
        assert len(productos) == 1
        assert productos[0].categoria == 'pantalla'

    def test_filtro_marca(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', marca='SAMSUNG'),
            Producto(nombre='P2', categoria='pantalla', marca='XIAOMI')
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(marca='SAMSUNG')
        assert len(productos) == 1
        assert productos[0].marca == 'SAMSUNG'

    def test_filtro_precio_min_bs(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', precio_mayor_bs=Decimal('100')),
            Producto(nombre='P2', categoria='pantalla', precio_mayor_bs=Decimal('50'))
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(precio_min=75)
        assert len(productos) == 1
        assert productos[0].precio_mayor_bs == Decimal('100')

    def test_filtro_precio_max_bs(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', precio_mayor_bs=Decimal('100')),
            Producto(nombre='P2', categoria='pantalla', precio_mayor_bs=Decimal('50'))
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(precio_max=75)
        assert len(productos) == 1
        assert productos[0].precio_mayor_bs == Decimal('50')

    def test_filtro_precio_rango_usd(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', precio_mayor_usd=Decimal('10')),
            Producto(nombre='P2', categoria='pantalla', precio_mayor_usd=Decimal('20')),
            Producto(nombre='P3', categoria='pantalla', precio_mayor_usd=Decimal('30'))
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(precio_min_usd=15, precio_max_usd=25)
        assert len(productos) == 1
        assert productos[0].precio_mayor_usd == Decimal('20')

    def test_filtro_proveedor(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', proveedor='Samsung Parts'),
            Producto(nombre='P2', categoria='pantalla', proveedor='Xiaomi Supply')
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(proveedor='Samsung')
        assert len(productos) == 1

    def test_filtro_stock_bajo_si(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', cantidad_stock=2, stock_minimo=5),
            Producto(nombre='P2', categoria='pantalla', cantidad_stock=20, stock_minimo=5)
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(stock_bajo='si')
        assert len(productos) == 1
        assert productos[0].nombre == 'P1'

    def test_filtro_stock_bajo_no(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', cantidad_stock=2, stock_minimo=5),
            Producto(nombre='P2', categoria='pantalla', cantidad_stock=20, stock_minimo=5)
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(stock_bajo='no')
        assert len(productos) == 1
        assert productos[0].nombre == 'P2'

    def test_filtro_stock_rango(self, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='pantalla', cantidad_stock=3),
            Producto(nombre='P2', categoria='pantalla', cantidad_stock=15),
            Producto(nombre='P3', categoria='pantalla', cantidad_stock=30)
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(stock_minimo=5, stock_maximo=20)
        assert len(productos) == 1
        assert productos[0].nombre == 'P2'

    def test_filtros_combinados(self, db):
        db.session.add_all([
            Producto(nombre='Pantalla S21', categoria='pantalla', marca='SAMSUNG', cantidad_stock=2, stock_minimo=5),
            Producto(nombre='Pantalla S22', categoria='pantalla', marca='SAMSUNG', cantidad_stock=20, stock_minimo=5),
            Producto(nombre='Pantalla Xiaomi', categoria='pantalla', marca='XIAOMI', cantidad_stock=2, stock_minimo=5)
        ])
        db.session.commit()
        productos = ProductoController.obtener_con_filtros(
            categoria='pantalla', marca='SAMSUNG', stock_bajo='si'
        )
        assert len(productos) == 1
        assert productos[0].nombre == 'Pantalla S21'


class TestObtenerPorId:
    def test_obtener_existente(self, db):
        producto = Producto(nombre='Test', categoria='otro')
        db.session.add(producto)
        db.session.commit()
        resultado = ProductoController.obtener_por_id(producto.id)
        assert resultado is not None
        assert resultado.nombre == 'Test'

    def test_obtener_no_existente(self, db):
        resultado = ProductoController.obtener_por_id(999)
        assert resultado is None

    def test_obtener_con_modelos(self, db):
        modelo = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
        db.session.add(modelo)
        db.session.flush()
        producto = Producto(nombre='Pantalla', categoria='pantalla')
        producto.modelos_compatibles.append(modelo)
        db.session.add(producto)
        db.session.commit()
        resultado = ProductoController.obtener_por_id(producto.id)
        assert resultado is not None
        assert len(resultado.modelos_compatibles) == 1


class TestCrear:
    def test_crear_minimo(self, db):
        data = {
            'nombre': 'Nuevo Producto',
            'categoria': 'otro',
            'cantidad_stock': 10,
            'stock_minimo': 5
        }
        producto = ProductoController.crear(data)
        assert producto.id is not None
        assert producto.nombre == 'Nuevo Producto'

    def test_crear_completo(self, db):
        data = {
            'nombre': 'Pantalla AMOLED',
            'descripcion': '6.5 pulgadas',
            'categoria': 'pantalla',
            'marca': 'SAMSUNG',
            'cantidad_stock': 50,
            'stock_minimo': 10,
            'proveedor': 'Samsung Co',
            'precio_mayor_bs': Decimal('1000'),
            'precio_mayor_usd': Decimal('100'),
            'precio_detal_bs': Decimal('1200'),
            'precio_detal_usd': Decimal('120'),
            'precio_tecnico_bs': Decimal('800'),
            'precio_tecnico_usd': Decimal('80')
        }
        producto = ProductoController.crear(data)
        assert producto.precio_mayor_bs == Decimal('1000')
        assert producto.precio_tecnico_usd == Decimal('80')

    def test_crear_con_modelos(self, db):
        m1 = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
        m2 = ModeloTelefono(nombre='Galaxy S22', marca='SAMSUNG')
        db.session.add_all([m1, m2])
        db.session.commit()
        data = {
            'nombre': 'Pantalla Galaxy',
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        }
        producto = ProductoController.crear(data, modelos_ids=[m1.id, m2.id])
        assert len(producto.modelos_compatibles) == 2

    def test_crear_sin_modelos(self, db):
        data = {
            'nombre': 'Cable USB',
            'categoria': 'cable',
            'cantidad_stock': 100,
            'stock_minimo': 10
        }
        producto = ProductoController.crear(data)
        assert len(producto.modelos_compatibles) == 0


class TestActualizar:
    def test_actualizar_existente(self, db):
        producto = Producto(nombre='Viejo', categoria='otro', cantidad_stock=5, stock_minimo=5)
        db.session.add(producto)
        db.session.commit()
        data = {
            'nombre': 'Nuevo',
            'categoria': 'pantalla',
            'cantidad_stock': 20,
            'stock_minimo': 10
        }
        resultado = ProductoController.actualizar(producto.id, data)
        assert resultado is not None
        assert resultado.nombre == 'Nuevo'
        assert resultado.categoria == 'pantalla'

    def test_actualizar_no_existente(self, db):
        data = {'nombre': 'Test', 'categoria': 'otro', 'cantidad_stock': 1, 'stock_minimo': 1}
        resultado = ProductoController.actualizar(999, data)
        assert resultado is None

    def test_actualizar_con_modelos(self, db):
        producto = Producto(nombre='Pantalla', categoria='pantalla', cantidad_stock=10, stock_minimo=5)
        modelo = ModeloTelefono(nombre='Galaxy S21', marca='SAMSUNG')
        db.session.add_all([producto, modelo])
        db.session.commit()
        data = {
            'nombre': 'Pantalla Actualizada',
            'categoria': 'pantalla',
            'cantidad_stock': 10,
            'stock_minimo': 5
        }
        resultado = ProductoController.actualizar(producto.id, data, modelos_ids=[modelo.id])
        assert resultado is not None
        assert len(resultado.modelos_compatibles) == 1

    def test_actualizar_parcial(self, db):
        producto = Producto(
            nombre='Test', categoria='otro',
            cantidad_stock=10, stock_minimo=5,
            precio_mayor_bs=Decimal('100')
        )
        db.session.add(producto)
        db.session.commit()
        data = {
            'nombre': 'Test',
            'categoria': 'otro',
            'cantidad_stock': 10,
            'stock_minimo': 5,
            'precio_mayor_bs': Decimal('200')
        }
        resultado = ProductoController.actualizar(producto.id, data)
        assert resultado.precio_mayor_bs == Decimal('200')


class TestEliminar:
    def test_eliminar_existente(self, db):
        producto = Producto(nombre='Eliminar', categoria='otro')
        db.session.add(producto)
        db.session.commit()
        resultado = ProductoController.eliminar(producto.id)
        assert resultado is True
        assert Producto.query.get(producto.id) is None

    def test_eliminar_no_existente(self, db):
        resultado = ProductoController.eliminar(999)
        assert resultado is False


class TestActualizarStockRapido:
    def test_actualizar_stock_valido(self, db):
        producto = Producto(nombre='Test', categoria='otro', cantidad_stock=10)
        db.session.add(producto)
        db.session.commit()
        resultado = ProductoController.actualizar_stock_rapido(producto.id, 25)
        assert resultado is True
        producto_actualizado = Producto.query.get(producto.id)
        assert producto_actualizado.cantidad_stock == 25

    def test_actualizar_stock_no_existente(self, db):
        resultado = ProductoController.actualizar_stock_rapido(999, 10)
        assert resultado is False

    def test_actualizar_stock_a_cero(self, db):
        producto = Producto(nombre='Test', categoria='otro', cantidad_stock=10)
        db.session.add(producto)
        db.session.commit()
        resultado = ProductoController.actualizar_stock_rapido(producto.id, 0)
        assert resultado is True
        producto_actualizado = Producto.query.get(producto.id)
        assert producto_actualizado.cantidad_stock == 0
