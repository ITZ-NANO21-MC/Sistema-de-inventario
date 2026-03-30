import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

load_dotenv(dotenv_path=env_path, override=True)  # Carga variables de entorno desde .env y sobrescribe

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-para-desarrollo'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///inventario.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Configuración de Flask-APScheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'America/Caracas'  # UTC-4, hora de Venezuela
    
    # Configuración de Jobs - Alerta Stock Bajo
    JOB_ALERTA_STOCK_HORA = int(os.environ.get('JOB_ALERTA_STOCK_HORA', 8))
    JOB_ALERTA_STOCK_MINUTO = int(os.environ.get('JOB_ALERTA_STOCK_MINUTO', 0))
    JOB_ALERTA_STOCK_ACTIVO = os.environ.get('JOB_ALERTA_STOCK_ACTIVO', 'true').lower() in ['true', '1']
    
    # Configuración de Jobs - Informe General Mañana
    JOB_INFORME_MANANA_HORA = int(os.environ.get('JOB_INFORME_MANANA_HORA', 7))
    JOB_INFORME_MANANA_MINUTO = int(os.environ.get('JOB_INFORME_MANANA_MINUTO', 0))
    JOB_INFORME_MANANA_ACTIVO = os.environ.get('JOB_INFORME_MANANA_ACTIVO', 'true').lower() in ['true', '1']
    
    # Configuración de Jobs - Informe General Tarde
    JOB_INFORME_TARDE_HORA = int(os.environ.get('JOB_INFORME_TARDE_HORA', 19))
    JOB_INFORME_TARDE_MINUTO = int(os.environ.get('JOB_INFORME_TARDE_MINUTO', 0))
    JOB_INFORME_TARDE_ACTIVO = os.environ.get('JOB_INFORME_TARDE_ACTIVO', 'true').lower() in ['true', '1']
    
    # Configuración de Jobs - Respaldo Diario
    JOB_BACKUP_HORA = int(os.environ.get('JOB_BACKUP_HORA', 21))
    JOB_BACKUP_MINUTO = int(os.environ.get('JOB_BACKUP_MINUTO', 0))
    JOB_BACKUP_ACTIVO = os.environ.get('JOB_BACKUP_ACTIVO', 'true').lower() in ['true', '1']
    
    # Configuración de Tasa de Cambio
    TASA_CAMBIO_USD_BS = float(os.environ.get('TASA_CAMBIO_USD_BS', 0))
    
    # Otras configuraciones globales