import os
from app import create_app, db

app = create_app()
with app.app_context():
    # Verificar si la base de datos ya existe
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        db.create_all()
        print("Base de datos creada.")
    else:
        print("La base de datos ya existe.")

if __name__ == '__main__':
    app.run(debug=True)