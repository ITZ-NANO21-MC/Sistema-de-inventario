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
            'prefix': prefix,
            'nombre': config['nombre'],
            'descripcion': config['descripcion'],
            'hora': int(os.environ.get(f'{prefix}_HORA', 0)),
            'minuto': int(os.environ.get(f'{prefix}_MINUTO', 0)),
            'activo': os.environ.get(f'{prefix}_ACTIVO', 'true').lower() in ['true', '1']
        }
        jobs.append(job_data)
    
    # Obtener tasa de cambio
    tasa_cambio = os.environ.get('TASA_CAMBIO_USD_BS', '0')
    
    return render_template('config/jobs.html', jobs=jobs, tasa_cambio=tasa_cambio)


@config_bp.route('/configuracion/jobs/actualizar', methods=['POST'])
def actualizar_jobs():
    """Guarda la configuración en archivo .env."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    jobs_to_update = ['alerta_stock_diaria', 'informe_general_manana', 'informe_general_tarde']
    
    scheduler = current_app.extensions.get('scheduler')
    
    for job_id in jobs_to_update:
        prefix = JOBS_CONFIG[job_id]['prefix']
        
        hora_key = f'{prefix}_HORA'
        minuto_key = f'{prefix}_MINUTO'
        activo_key = f'{prefix}_ACTIVO'
        
        hora = request.form.get(hora_key, '0')
        minuto = request.form.get(minuto_key, '0')
        activo = 'true' if activo_key in request.form else 'false'
        
        update_env_value(env_path, hora_key, hora)
        os.environ[hora_key] = str(hora)
        
        update_env_value(env_path, minuto_key, minuto)
        os.environ[minuto_key] = str(minuto)
        
        update_env_value(env_path, activo_key, activo)
        os.environ[activo_key] = str(activo)
        
        # Aplicar cambios al scheduler de inmediato si está activo
        if scheduler:
            job = scheduler.get_job(job_id)
            if activo == 'true':
                if job:
                    scheduler.resume_job(job_id)
                    scheduler.reschedule_job(job_id, trigger='cron', hour=int(hora), minute=int(minuto))
                else:
                    # Si no existe, lo agregamos llamando a la función correspondiente
                    from app.services.alertas import verificar_stock_y_notificar, generar_informe_general
                    func = verificar_stock_y_notificar if job_id == 'alerta_stock_diaria' else generar_informe_general
                    scheduler.add_job(
                        id=job_id,
                        func=func,
                        args=[current_app._get_current_object()],
                        trigger='cron',
                        hour=int(hora),
                        minute=int(minuto)
                    )
            else:
                if job:
                    scheduler.pause_job(job_id)
    
    # Guardar tasa de cambio
    tasa_cambio = request.form.get('tasa_cambio', '0')
    update_env_value(env_path, 'TASA_CAMBIO_USD_BS', tasa_cambio)
    os.environ['TASA_CAMBIO_USD_BS'] = str(tasa_cambio)
    
    flash('Configuración guardada y jobs actualizados con éxito.', 'success')
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
