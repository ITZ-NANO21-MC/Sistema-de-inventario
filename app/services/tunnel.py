"""
Servicio de Estado del Túnel.
Gestiona la información del túnel activo (URL, tipo, estado).
"""
import os
import json
import time
from pathlib import Path


TUNNEL_STATUS_FILE = '.tunnel_status'


def get_project_root():
    """Encuentra la raíz del proyecto."""
    return Path(__file__).resolve().parent.parent.parent


def get_tunnel_status():
    """
    Obtiene el estado actual del túnel.
    
    Returns:
        dict: Estado del túnel con claves 'activo', 'url', 'tipo', 'timestamp'
    """
    project_root = get_project_root()
    status_file = project_root / TUNNEL_STATUS_FILE
    
    # Primero verificar variable de entorno
    tunnel_url = os.environ.get('TUNNEL_URL')
    tunnel_type = os.environ.get('TUNNEL_TYPE', '')
    
    if tunnel_url:
        return {
            'activo': True,
            'url': tunnel_url,
            'tipo': tunnel_type or 'cloudflared',
            'timestamp': time.time()
        }
    
    # Luego verificar archivo de estado
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                data = json.load(f)
            
            # Verificar que el estado no sea muy antiguo (5 minutos)
            if time.time() - data.get('timestamp', 0) < 300:
                return data
        except (json.JSONDecodeError, IOError):
            pass
    
    return {
        'activo': False,
        'url': None,
        'tipo': None,
        'timestamp': 0
    }


def save_tunnel_status(url, tunnel_type='cloudflared'):
    """
    Guarda el estado del túnel en un archivo.
    
    Args:
        url: URL pública del túnel
        tunnel_type: Tipo de túnel ('cloudflared' o 'zrok')
    """
    project_root = get_project_root()
    status_file = project_root / TUNNEL_STATUS_FILE
    
    data = {
        'activo': True,
        'url': url,
        'tipo': tunnel_type,
        'timestamp': time.time()
    }
    
    try:
        with open(status_file, 'w') as f:
            json.dump(data, f)
        return True
    except IOError:
        return False


def clear_tunnel_status():
    """Elimina el archivo de estado del túnel."""
    project_root = get_project_root()
    status_file = project_root / TUNNEL_STATUS_FILE
    
    if status_file.exists():
        try:
            status_file.unlink()
            return True
        except IOError:
            pass
    return False
