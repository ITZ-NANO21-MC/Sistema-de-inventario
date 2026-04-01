"""
Rutas del estado del túnel.
Muestra información del túnel activo y permite gestionarlo.
"""
from flask import Blueprint, jsonify, request
from app.services.tunnel import get_tunnel_status, save_tunnel_status, clear_tunnel_status
from flask_login import login_required

tunnel_bp = Blueprint('tunnel', __name__)


@tunnel_bp.route('/api/tunnel/status')
@login_required
def api_status():
    """API: Obtiene el estado actual del túnel."""
    status = get_tunnel_status()
    return jsonify(status)


@tunnel_bp.route('/api/tunnel/register', methods=['POST'])
def api_register():
    """API: Registra manualmente una URL de túnel."""
    data = request.get_json()
    url = data.get('url', '')
    tunnel_type = data.get('tipo', 'cloudflared')
    
    if not url:
        return jsonify({'error': 'URL requerida'}), 400
    
    save_tunnel_status(url, tunnel_type)
    return jsonify({'activo': True, 'url': url, 'tipo': tunnel_type})


@tunnel_bp.route('/api/tunnel/clear', methods=['POST'])
@login_required
def api_clear():
    """API: Limpia el estado del túnel."""
    clear_tunnel_status()
    return jsonify({'activo': False})
