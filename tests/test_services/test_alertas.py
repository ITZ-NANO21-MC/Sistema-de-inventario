from decimal import Decimal
from unittest.mock import patch, MagicMock
from app.services.alertas import (
    verificar_stock_y_notificar,
    enviar_alerta_email,
    generar_informe_general,
    enviar_informe_general_email,
    realizar_backup_automatico
)
from app.models import Producto


class TestVerificarStockYNotificar:
    def test_con_productos_bajos(self, app, db):
        db.session.add(Producto(nombre='P1', categoria='otro', cantidad_stock=2, stock_minimo=5))
        db.session.commit()
        with patch('app.services.alertas.enviar_alerta_email') as mock_enviar:
            verificar_stock_y_notificar(app)
            mock_enviar.assert_called_once()
            productos_enviados = mock_enviar.call_args[0][1]
            assert len(productos_enviados) == 1

    def test_sin_productos_bajos(self, app, db):
        db.session.add(Producto(nombre='P1', categoria='otro', cantidad_stock=20, stock_minimo=5))
        db.session.commit()
        with patch('app.services.alertas.enviar_alerta_email') as mock_enviar:
            verificar_stock_y_notificar(app)
            mock_enviar.assert_not_called()

    def test_sin_productos(self, app, db):
        with patch('app.services.alertas.enviar_alerta_email') as mock_enviar:
            verificar_stock_y_notificar(app)
            mock_enviar.assert_not_called()


class TestEnviarAlertaEmail:
    def test_enviar_alerta_exito(self, app):
        productos = [Producto(nombre='Test', cantidad_stock=1, stock_minimo=5)]
        with patch('app.mail') as mock_mail:
            with app.app_context():
                enviar_alerta_email(app, productos)
                mock_mail.send.assert_called_once()

    def test_enviar_alerta_error(self, app):
        productos = [Producto(nombre='Test', cantidad_stock=1, stock_minimo=5)]
        with patch('app.mail') as mock_mail:
            mock_mail.send.side_effect = Exception('Connection failed')
            with app.app_context():
                enviar_alerta_email(app, productos)
                mock_mail.send.assert_called_once()


class TestGenerarInformeGeneral:
    def test_informe_con_productos(self, app, db):
        db.session.add_all([
            Producto(nombre='P1', categoria='otro', cantidad_stock=20),
            Producto(nombre='P2', categoria='otro', cantidad_stock=2, stock_minimo=5)
        ])
        db.session.commit()
        with patch('app.services.alertas.enviar_informe_general_email') as mock_enviar:
            generar_informe_general(app)
            mock_enviar.assert_called_once()
            args = mock_enviar.call_args[0]
            assert len(args[1]) == 2
            stats = args[2]
            assert stats['total_productos'] == 2
            assert stats['total_stock'] == 22
            assert stats['productos_bajos'] == 1
            assert stats['productos_ok'] == 1

    def test_informe_sin_productos(self, app, db):
        with patch('app.services.alertas.enviar_informe_general_email') as mock_enviar:
            generar_informe_general(app)
            mock_enviar.assert_called_once()
            args = mock_enviar.call_args[0]
            assert len(args[1]) == 0
            assert args[2]['total_productos'] == 0


class TestEnviarInformeGeneralEmail:
    def test_enviar_informe_exito(self, app):
        productos = [Producto(nombre='Test', cantidad_stock=10, stock_minimo=5)]
        estadisticas = {
            'total_productos': 1,
            'total_stock': 10,
            'productos_bajos': 0,
            'productos_ok': 1,
            'periodo': 'Manana (7:00 AM)'
        }
        with patch('app.mail') as mock_mail:
            with app.app_context():
                enviar_informe_general_email(app, productos, estadisticas)
                mock_mail.send.assert_called_once()

    def test_enviar_informe_error(self, app):
        productos = [Producto(nombre='Test', cantidad_stock=10, stock_minimo=5)]
        estadisticas = {'total_productos': 1, 'total_stock': 10, 'productos_bajos': 0, 'productos_ok': 1, 'periodo': 'Tarde (7:00 PM)'}
        with patch('app.mail') as mock_mail:
            mock_mail.send.side_effect = Exception('SMTP error')
            with app.app_context():
                enviar_informe_general_email(app, productos, estadisticas)
                mock_mail.send.assert_called_once()


class TestRealizarBackupAutomatico:
    def test_backup_uri_no_sqlite(self, app):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/db'
        with patch('app.mail') as mock_mail:
            realizar_backup_automatico(app)
            mock_mail.send.assert_not_called()

    def test_backup_archivo_no_existe(self, app):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///no_existe.db'
        with patch('app.mail') as mock_mail:
            with patch('os.path.exists', return_value=False):
                realizar_backup_automatico(app)
                mock_mail.send.assert_not_called()

    def test_backup_exito(self, app, db):
        db.session.add(Producto(nombre='Test', categoria='otro'))
        db.session.commit()
        with patch('app.mail') as mock_mail:
            with patch('os.path.exists', return_value=True):
                realizar_backup_automatico(app)
                mock_mail.send.assert_called_once()
                msg = mock_mail.send.call_args[0][0]
                assert len(msg.attachments) == 1
                assert msg.attachments[0].filename.startswith('respaldo_inventario_')
