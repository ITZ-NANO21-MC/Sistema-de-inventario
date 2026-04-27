"""
Módulo de Auditoría de Seguridad.
Registra eventos críticos del sistema en un archivo de log rotativo.
"""
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask_login import current_user
import os

# Logger dedicado para auditoría de seguridad
audit_logger = logging.getLogger('security_audit')

def configurar_audit_logger(app):
    """Configura el logger de auditoría con rotación de archivos."""
    from config import get_data_dir
    log_dir = os.path.join(get_data_dir(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'security.log')
    
    # Archivo rotativo: máximo 5MB por archivo, mantener 5 archivos de respaldo
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)

def registrar_evento(accion, detalle='', usuario=None):
    """
    Registra un evento de auditoría.
    
    Args:
        accion: Tipo de acción (LOGIN_EXITOSO, LOGIN_FALLIDO, ELIMINAR_PRODUCTO, etc.)
        detalle: Descripción adicional del evento.
        usuario: Nombre de usuario. Si no se proporciona, se usa el usuario actual.
    """
    if usuario is None:
        try:
            usuario = current_user.username if current_user.is_authenticated else 'anónimo'
        except:
            usuario = 'sistema'
    
    audit_logger.info(f"USUARIO={usuario} | ACCION={accion} | {detalle}")
