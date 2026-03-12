import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables de entorno desde .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-para-desarrollo'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///inventario.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Otras configuraciones globales