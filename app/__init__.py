from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_apscheduler import APScheduler
from config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
scheduler = APScheduler()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Configuración de APScheduler
    scheduler.init_app(app)
    
    # Programar jobs usando configuración dinámica
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
    
    # Ejemplo alternativo de prueba: se ejecutaría cada minuto
    #scheduler.add_job(id='test_alerta', func=verificar_stock_y_notificar, args=[app], trigger='interval', minutes=1)
    
    scheduler.start()

    # Registro de blueprints
    from app.views.producto_routes import producto_bp
    from app.views.modelo_routes import modelo_bp
    from app.views.config_routes import config_bp
    from app.views.alertas_routes import alertas_bp

    app.register_blueprint(producto_bp, url_prefix='/productos')
    app.register_blueprint(modelo_bp, url_prefix='/modelos')
    app.register_blueprint(config_bp)
    app.register_blueprint(alertas_bp)

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

    # Ruta raíz redirige a lista de productos
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('producto.listar'))

    return app
