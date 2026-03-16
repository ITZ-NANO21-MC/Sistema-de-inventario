from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
import os
from dotenv import load_dotenv

config_bp = Blueprint('config', __name__, template_folder='../templates/config')

load_dotenv()

JOBS_CONFIG = {
    'alerta_stock_diaria': {
        'nombre': 'Alerta Stock Bajo',
        'prefix': 'JOB_ALERTA_STOCK',
        'descripcion': 'Envía una alerta cuando productos tienen stock bajo del mínimo'
    },
    'informe_general_manana': {
        'nombre': 'Informe General Mañana',
        'prefix': 'JOB_INFORME_MANANA',
        'descripcion': 'Envía un informe completo del inventario por la mañana'
    },
    'informe_general_tarde': {
        'nombre': 'Informe General Tarde',
        'prefix': 'JOB_INFORME_TARDE',
        'descripcion': 'Envía un informe completo del inventario por la tarde'
    }
}


@config_bp.route('/configuracion')
def panel():
    jobs = []
    for job_id, config in JOBS_CONFIG.items():
        prefix = config['prefix']
        job_data = {
            'id': job_id,
            'nombre': config['nombre'],
            'descripcion': config['descripcion'],
            'hora': int(os.environ.get(f'{prefix}_HORA', 0)),
            'minuto': int(os.environ.get(f'{prefix}_MINUTO', 0)),
            'activo': os.environ.get(f'{prefix}_ACTIVO', 'true').lower() in ['true', '1']
        }
        jobs.append(job_data)
    return render_template('config/jobs.html', jobs=jobs)


@config_bp.route('/configuracion/jobs/actualizar', methods=['POST'])
def actualizar_jobs():
    """Guarda la configuración en archivo .env."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    jobs_to_update = ['alerta_stock_diaria', 'informe_general_manana', 'informe_general_tarde']
    
    for job_id in jobs_to_update:
        prefix = JOBS_CONFIG[job_id]['prefix']
        
        hora_key = f'{prefix}_HORA'
        minuto_key = f'{prefix}_MINUTO'
        activo_key = f'{prefix}_ACTIVO'
        
        hora = request.form.get(hora_key, '0')
        minuto = request.form.get(minuto_key, '0')
        activo = 'true' if activo_key in request.form else 'false'
        
        update_env_value(env_path, hora_key, hora)
        update_env_value(env_path, minuto_key, minuto)
        update_env_value(env_path, activo_key, activo)
    
    flash('Configuración guardada en .env. Reinicia la aplicación para aplicar los cambios.', 'success')
    return redirect(url_for('config.panel'))


def update_env_value(env_path, key, value):
    """Actualiza o agrega una variable en el archivo .env."""
    lines = []
    found = False
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith(f'{key}='):
                    lines.append(f'{key}={value}\n')
                    found = True
                else:
                    lines.append(line)
    
    if not found:
        lines.append(f'{key}={value}\n')
    
    with open(env_path, 'w') as f:
        f.writelines(lines)
