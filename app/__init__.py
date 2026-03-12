from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Registro de blueprints
    from app.views.producto_routes import producto_bp
    app.register_blueprint(producto_bp, url_prefix='/productos')

    # Ruta raíz redirige a lista de productos
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('producto.listar'))

    return app