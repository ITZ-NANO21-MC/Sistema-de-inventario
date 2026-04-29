from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_talisman import Talisman
from config import Config
import os
import sys

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
scheduler = APScheduler()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    from config import get_data_dir
    instance_path = os.path.join(get_data_dir(), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    app = Flask(__name__, instance_path=instance_path)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    # Configuración de CSP para Talisman (Mantiene la UI offline funcionando)
    csp = {
        'default-src': ['\'self\''],
        'script-src': ['\'self\'', '\'unsafe-inline\''],
        'style-src': ['\'self\'', '\'unsafe-inline\''],
        'img-src': ['\'self\'', 'data:'],
        'font-src': ['\'self\'']
    }
    
    # Iniciar Talisman. HTTPS solo se fuerza si se configura explícitamente en .env
    # Para el servidor de desarrollo Flask (HTTP), FORCE_HTTPS debe ser False.
    force_https = os.environ.get('FORCE_HTTPS', 'False').lower() in ['true', '1', 't']
    Talisman(app, content_security_policy=csp, force_https=force_https)

    # Configuración del Logger de Auditoría de Seguridad
    from app.services.audit import configurar_audit_logger
    configurar_audit_logger(app)

    # Aplicar migraciones automáticamente al inicio
    with app.app_context():
        from flask_migrate import upgrade, stamp
        from sqlalchemy import inspect
        try:
            # Determinar la ruta de migraciones según el entorno
            if getattr(sys, 'frozen', False):
                migrations_dir = os.path.join(sys._MEIPASS, 'migrations')
            else:
                migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'migrations')
            
            # Verificar si la base de datos es nueva (sin tablas)
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            
            if not tablas_existentes or 'productos' not in tablas_existentes:
                # DB nueva: crear todas las tablas desde los modelos y marcar
                # la migración en HEAD para que no intente ALTER sobre lo que
                # acaba de crear.
                app.logger.info("Base de datos nueva detectada. Creando esquema completo...")
                db.create_all()
                stamp(directory=migrations_dir)
                app.logger.info("Esquema creado y migraciones marcadas en HEAD.")
            else:
                # DB existente: aplicar migraciones pendientes normalmente
                upgrade(directory=migrations_dir)
                app.logger.info("Migraciones de base de datos comprobadas/aplicadas correctamente.")
        except Exception as e:
            app.logger.error(f"Error al aplicar migraciones automáticas: {e}")

    # Configuración de APScheduler
    scheduler.init_app(app)

    # Registrar y arrancar jobs del scheduler.
    # En modo debug, Werkzeug lanza 2 procesos (padre watcher + hijo servidor).
    # Solo registramos jobs en el hijo (WERKZEUG_RUN_MAIN='true') para evitar
    # duplicados. En producción (PyInstaller/Electron) no hay reloader, así
    # que siempre registramos.
    is_reloader_parent = (
        os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
        and os.environ.get('WERKZEUG_RUN_MAIN') != 'true'
    )
    
    if not is_reloader_parent:
        from app.services.alertas import verificar_stock_y_notificar, generar_informe_general
        
        # Alerta de stock bajo - configurable desde .env
        if app.config.get('JOB_ALERTA_STOCK_ACTIVO', True):
            scheduler.add_job(
                id='alerta_stock_diaria',
                func=verificar_stock_y_notificar,
                args=[app],
                trigger='cron',
                hour=app.config.get('JOB_ALERTA_STOCK_HORA', 8),
                minute=app.config.get('JOB_ALERTA_STOCK_MINUTO', 0)
            )
        
        # Informe general de la mañana - configurable desde .env
        if app.config.get('JOB_INFORME_MANANA_ACTIVO', True):
            scheduler.add_job(
                id='informe_general_manana',
                func=generar_informe_general,
                args=[app],
                trigger='cron',
                hour=app.config.get('JOB_INFORME_MANANA_HORA', 7),
                minute=app.config.get('JOB_INFORME_MANANA_MINUTO', 0)
            )
        
        # Informe general de la tarde - configurable desde .env
        if app.config.get('JOB_INFORME_TARDE_ACTIVO', True):
            scheduler.add_job(
                id='informe_general_tarde',
                func=generar_informe_general,
                args=[app],
                trigger='cron',
                hour=app.config.get('JOB_INFORME_TARDE_HORA', 19),
                minute=app.config.get('JOB_INFORME_TARDE_MINUTO', 0)
            )
            
        # Respaldo diario de base de datos - configurable desde .env
        if app.config.get('JOB_BACKUP_ACTIVO', True):
            # Se requiere importar aquí para evitar ciclos si está en otro lado
            from app.services.alertas import realizar_backup_automatico
            scheduler.add_job(
                id='backup_diario',
                func=realizar_backup_automatico,
                args=[app],
                trigger='cron',
                hour=app.config.get('JOB_BACKUP_HORA', 21), # Default 9:00 PM
                minute=app.config.get('JOB_BACKUP_MINUTO', 0)
            )
        
        scheduler.start()
        app.logger.info("APScheduler iniciado correctamente con los jobs configurados.")

    # Registro de blueprints
    from app.views.producto_routes import producto_bp
    from app.views.modelo_routes import modelo_bp
    from app.views.config_routes import config_bp
    from app.views.alertas_routes import alertas_bp
    from app.views.auth_routes import auth_bp
    from app.views.tunnel_routes import tunnel_bp

    app.register_blueprint(producto_bp, url_prefix='/productos')
    app.register_blueprint(modelo_bp, url_prefix='/modelos')
    app.register_blueprint(config_bp)
    app.register_blueprint(alertas_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tunnel_bp)

    # Cargar usuario para Flask-Login
    from app.models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Context processor para pasar productos_bajos_count a todas las plantillas
    @app.context_processor
    def inject_productos_bajos():
        from app.models import Producto
        try:
            count = Producto.query.filter(
                Producto.cantidad_stock <= Producto.stock_minimo
            ).count()
        except:
            count = 0
        return dict(productos_bajos_count=count)

    # Context processor para pasar estado del túnel a todas las plantillas
    @app.context_processor
    def inject_tunnel_status():
        from app.services.tunnel import get_tunnel_status
        return dict(tunnel_status=get_tunnel_status())

    # Ruta raíz redirige a lista de productos
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('producto.listar'))

    return app
