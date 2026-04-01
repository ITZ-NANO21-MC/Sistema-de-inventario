from app.models import Producto
from flask_mail import Message
from flask import render_template
import os
from datetime import datetime

def verificar_stock_y_notificar(app):
    """
    Función que consulta todos los productos y verifica si alguno tiene
    un stock menor o igual al mínimo. Si los hay, envía un correo.
    Se requiere pasar la instancia `app` de Flask porque esta función
    se ejecuta fuera del contexto de una petición normal web.
    """
    with app.app_context():
        # Consulta óptima filtrando directamente en la base de datos
        productos_bajos = Producto.query.filter(Producto.cantidad_stock <= Producto.stock_minimo).all()
        
        if productos_bajos:
            app.logger.info(f"Se encontraron {len(productos_bajos)} productos con stock bajo. Enviando alerta...")
            enviar_alerta_email(app, productos_bajos)
        else:
            app.logger.info("Stock verificado: Todos los productos tienen niveles adecuados.")

def enviar_alerta_email(app, productos):
    from app import mail  # Importación local para evitar ciclos
    
    # Renderizamos la plantilla HTML con los productos
    html_body = render_template('email/alerta_stock.html', productos=productos)
    
    # Configuramos el mensaje
    asunto = f"⚠️ Alerta de Inventario: {len(productos)} productos con stock bajo"
    destinatario = os.environ.get('MAIL_DEFAULT_SENDER') # En nuestro plan enviamos al mismo admin
    
    msg = Message(
        subject=asunto,
        recipients=[destinatario],
        html=html_body
    )
    
    try:
        mail.send(msg)
        app.logger.info("Correo de alerta de stock enviado exitosamente.")
    except Exception as e:
        app.logger.error(f"Error al enviar el correo de alerta: {str(e)}")


def generar_informe_general(app):
    """
    Consulta TODOS los productos y genera un informe completo
    del estado del inventario, enviándolo por correo.
    """
    with app.app_context():
        todos_los_productos = Producto.query.all()
        
        # Calcular estadísticas
        total_productos = len(todos_los_productos)
        total_stock = sum(p.cantidad_stock for p in todos_los_productos)
        productos_bajos = [p for p in todos_los_productos if p.cantidad_stock <= p.stock_minimo]
        productos_ok = total_productos - len(productos_bajos)
        
        # Determinar si es informe AM o PM
        hora_actual = datetime.now().hour
        periodo = "Mañana (7:00 AM)" if hora_actual < 12 else "Tarde (7:00 PM)"
        
        estadisticas = {
            'total_productos': total_productos,
            'total_stock': total_stock,
            'productos_bajos': len(productos_bajos),
            'productos_ok': productos_ok,
            'periodo': periodo
        }
        
        enviar_informe_general_email(app, todos_los_productos, estadisticas)


def enviar_informe_general_email(app, productos, estadisticas):
    from app import mail
    from flask import render_template
    import os
    
    html_body = render_template(
        'email/informe_general.html', 
        productos=productos, 
        estadisticas=estadisticas,
        ahora=datetime.now()
    )
    
    asunto = f"📊 Informe de Inventario - {estadisticas['periodo']} - {len(productos)} productos"
    destinatario = os.environ.get('MAIL_DEFAULT_SENDER')
    
    msg = Message(subject=asunto, recipients=[destinatario], html=html_body)
    
    try:
        mail.send(msg)
        app.logger.info(f"Informe general ({estadisticas['periodo']}) enviado exitosamente.")
    except Exception as e:
        app.logger.error(f"Error al enviar informe general: {str(e)}")

def realizar_backup_automatico(app):
    """
    Realiza un respaldo de la base de datos (inventario.db),
    lo comprime en un .zip y lo envía por correo electrónico al administrador.
    """
    from app import mail
    from flask_mail import Message
    import os
    import zipfile
    from datetime import datetime
    import io

    with app.app_context():
        # Ruta dinámica a la base de datos
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not db_uri.startswith('sqlite:///'):
            app.logger.error("El backup automático solo soporta bases de datos SQLite locales.")
            return

        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.instance_path, db_path)
            
        if not os.path.exists(db_path):
            app.logger.error(f"Archivo de base de datos no encontrado en {db_path}.")
            return

        # Crear nombre de archivo basado en fecha y hora
        fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_filename = f"respaldo_inventario_{fecha_str}.zip"
        
        # Comprimir en memoria usando BytesIO
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(db_path, arcname=f"inventario_{fecha_str}.db")
        
        mem_zip.seek(0)
        
        # Preparar email
        asunto = f"💾 Respaldo de Base de Datos - {datetime.now().strftime('%Y-%m-%d')}"
        destinatario = os.environ.get('MAIL_DEFAULT_SENDER')
        
        # Cuerpo simple, o plantilla
        html_body = f"""
        <h3>Respaldo del Sistema de Inventario</h3>
        <p>Adjunto encontrarás el respaldo de la base de datos generado el <strong>{datetime.now().strftime('%d/%m/%Y a las %I:%M %p')}</strong>.</p>
        <p>Este archivo .zip contiene la base de datos SQLite con todos tus productos, categorías y stock actual.</p>
        <p><i>Guárdalo en un lugar seguro.</i></p>
        """
        
        msg = Message(subject=asunto, recipients=[destinatario], html=html_body)
        msg.attach(zip_filename, 'application/zip', mem_zip.read())
        
        try:
            mail.send(msg)
            app.logger.info("Respaldo de base de datos enviado por correo exitosamente.")
        except Exception as e:
            app.logger.error(f"Error al enviar correo de respaldo: {str(e)}")
