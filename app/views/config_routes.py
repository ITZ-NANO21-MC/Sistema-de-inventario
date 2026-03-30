from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
import os
from dotenv import load_dotenv
from config import Config

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
    },
    'backup_diario': {
        'nombre': 'Respaldo Diario (Backup)',
        'prefix': 'JOB_BACKUP',
        'descripcion': 'Envía una copia de la base de datos comprimida en .zip por correo'
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
    
    # Obtener configuración de correo
    mail_username = os.environ.get('MAIL_USERNAME', '')
    mail_default_sender = os.environ.get('MAIL_DEFAULT_SENDER', '')
    has_mail_password = bool(os.environ.get('MAIL_PASSWORD'))
    
    return render_template('config/jobs.html', jobs=jobs, tasa_cambio=tasa_cambio, 
                           mail_username=mail_username, mail_default_sender=mail_default_sender, 
                           has_mail_password=has_mail_password)


@config_bp.route('/configuracion/jobs/actualizar', methods=['POST'])
def actualizar_jobs():
    """Guarda la configuración en archivo .env."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    jobs_to_update = ['alerta_stock_diaria', 'informe_general_manana', 'informe_general_tarde', 'backup_diario']
    
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
                    from app.services.alertas import verificar_stock_y_notificar, generar_informe_general, realizar_backup_automatico
                    
                    if job_id == 'alerta_stock_diaria':
                        func = verificar_stock_y_notificar
                    elif job_id == 'backup_diario':
                        func = realizar_backup_automatico
                    else:
                        func = generar_informe_general
                        
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
    try:
        nueva_tasa = float(tasa_cambio)
        tasa_actual = float(os.environ.get('TASA_CAMBIO_USD_BS', '0'))
    except ValueError:
        nueva_tasa = 0
        tasa_actual = 0
        
    update_env_value(env_path, 'TASA_CAMBIO_USD_BS', tasa_cambio)
    os.environ['TASA_CAMBIO_USD_BS'] = str(tasa_cambio)
    Config.TASA_CAMBIO_USD_BS = nueva_tasa

    # Guardar configuración de correo
    mail_username = request.form.get('mail_username', '').strip()
    mail_password = request.form.get('mail_password', '').strip()
    mail_default_sender = request.form.get('mail_default_sender', '').strip()
    
    if mail_username:
        update_env_value(env_path, 'MAIL_USERNAME', mail_username)
        os.environ['MAIL_USERNAME'] = mail_username
        if 'mail' in current_app.extensions:
            current_app.extensions['mail'].username = mail_username

    if mail_password:
        update_env_value(env_path, 'MAIL_PASSWORD', mail_password)
        os.environ['MAIL_PASSWORD'] = mail_password
        if 'mail' in current_app.extensions:
            current_app.extensions['mail'].password = mail_password

    if mail_default_sender:
        update_env_value(env_path, 'MAIL_DEFAULT_SENDER', mail_default_sender)
        os.environ['MAIL_DEFAULT_SENDER'] = mail_default_sender
        if 'mail' in current_app.extensions:
            current_app.extensions['mail'].default_sender = mail_default_sender

    mensaje_extra = ""
    # Si la tasa cambió de forma válida, actualizar inventario
    if nueva_tasa > 0 and nueva_tasa != tasa_actual:
        from app.models import Producto
        from app import db
        productos = Producto.query.all()
        for p in productos:
            if p.precio_mayor_usd is not None:
                p.precio_mayor_bs = float(p.precio_mayor_usd) * nueva_tasa
            if p.precio_detal_usd is not None:
                p.precio_detal_bs = float(p.precio_detal_usd) * nueva_tasa
            if p.precio_tecnico_usd is not None:
                p.precio_tecnico_bs = float(p.precio_tecnico_usd) * nueva_tasa
        db.session.commit()
        mensaje_extra = f" Se actualizaron los precios en Bs de {len(productos)} productos."

    flash(f'Configuración guardada y jobs actualizados con éxito.{mensaje_extra}', 'success')
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

@config_bp.route('/configuracion/backup-manual')
def backup_manual():
    """Ruta para descargar la base de datos comprimida en .zip manualmente"""
    import zipfile
    import io
    from datetime import datetime
    from flask import send_file
    
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not db_uri.startswith('sqlite:///'):
        flash('El backup manual solo está disponible para bases de datos SQLite locales.', 'danger')
        return redirect(url_for('config.panel'))

    db_path = db_uri.replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        db_path = os.path.join(current_app.instance_path, db_path)
        
    if not os.path.exists(db_path):
        flash('No se encontró el archivo de base de datos.', 'danger')
        return redirect(url_for('config.panel'))
        
    fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_filename = f"respaldo_inventario_{fecha_str}.zip"
    
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_path, arcname=f"inventario_{fecha_str}.db")
        
    mem_zip.seek(0)
    
    return send_file(
        mem_zip,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )
