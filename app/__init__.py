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
    
    # Programar la alerta de stock bajo (por ejemplo: cada día a las 8 AM)
    from app.services.alertas import verificar_stock_y_notificar, generar_informe_general
    # Usando cron para ejecutar diariamente
    scheduler.add_job(
        id='alerta_stock_diaria',
        func=verificar_stock_y_notificar,
        args=[app],
        trigger='cron',
        hour=8,
        minute=0
    )
    
    # Informe general de la mañana - 7:00 AM
    scheduler.add_job(
        id='informe_general_manana',
        func=generar_informe_general,
        args=[app],
        trigger='cron',
        hour=7,
        minute=0
    )
    
    # Informe general de la tarde - 7:00 PM
    scheduler.add_job(
        id='informe_general_tarde',
        func=generar_informe_general,
        args=[app],
        trigger='cron',
        hour=19,
        minute=0
    )
    
    # Ejemplo alternativo de prueba: se ejecutaría cada minuto
    #scheduler.add_job(id='test_alerta', func=verificar_stock_y_notificar, args=[app], trigger='interval', minutes=1)
    
    scheduler.start()

    # Registro de blueprints
    from app.views.producto_routes import producto_bp
    from app.views.modelo_routes import modelo_bp

    app.register_blueprint(producto_bp, url_prefix='/productos')
    app.register_blueprint(modelo_bp, url_prefix='/modelos')

    # Ruta raíz redirige a lista de productos
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('producto.listar'))

    return app
