import os
import sys
from dotenv import load_dotenv


def get_data_dir():
    """Devuelve el directorio de datos persistentes.

    - PyInstaller (producción): carpeta 'data/' al lado del ejecutable real.
    - Desarrollo: el directorio del proyecto (donde está config.py).

    Returns:
        str: Ruta absoluta al directorio de datos.
    """
    if getattr(sys, 'frozen', False):
        # Modo PyInstaller: sys.executable apunta al .exe real (no al temporal)
        exe_dir = os.path.dirname(sys.executable)
        data_dir = os.path.join(exe_dir, 'data')
    else:
        # Modo desarrollo: el directorio donde está config.py
        data_dir = os.path.abspath(os.path.dirname(__file__))

    os.makedirs(data_dir, exist_ok=True)
    return data_dir


# Directorio de datos persistentes (usado por toda la aplicación)
DATA_DIR = get_data_dir()

# Cargar .env desde el directorio de datos
env_path = os.path.join(DATA_DIR, '.env')
load_dotenv(dotenv_path=env_path, override=True)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY == 'mi-clave-secreta-super-segura' or len(SECRET_KEY) < 32:
        raise ValueError("No se ha configurado una SECRET_KEY segura en las variables de entorno.")

    # Base de datos en DATA_DIR/instance/ para persistencia fuera del ejecutable
    _instance_dir = os.path.join(DATA_DIR, 'instance')
    os.makedirs(_instance_dir, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(_instance_dir, "inventario.db")}'
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