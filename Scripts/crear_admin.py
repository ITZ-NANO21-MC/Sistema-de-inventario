from flask import Flask
from config import Config
from app import db, create_app
from app.models import Usuario

app = create_app()

with app.app_context():
    # Asegurarnos de que las tablas existan
    db.create_all()
    
    # Comprobar si ya existe el administrador
    admin_user = Usuario.query.filter_by(username='admin').first()
    
    if not admin_user:
        print("Creando usuario administrador base...")
        admin = Usuario(username='admin', rol='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("¡Usuario 'admin' creado con éxito! Contraseña temporal: 'admin123'")
    else:
        print("El usuario 'admin' ya existe en el sistema.")
