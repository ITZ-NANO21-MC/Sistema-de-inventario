from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from app.controllers.alertas import AlertaController

from flask_login import login_required

alertas_bp = Blueprint('alertas', __name__)

@alertas_bp.before_request
@login_required
def require_login():
    pass


@alertas_bp.route('/alertas')
def listar():
    productos_bajos = AlertaController.obtener_productos_bajos()
    ultima_global = AlertaController.obtener_ultima_alerta_global()
    return render_template('alertas/index.html', 
                         productos=productos_bajos, 
                         ultima_global=ultima_global)


@alertas_bp.route('/alertas/enviar', methods=['POST'])
def enviar():
    from app.services.alertas import verificar_stock_y_notificar
    from app.controllers.alertas import AlertaController
    
    app = current_app._get_current_object()
    productos_bajos = AlertaController.obtener_productos_bajos()
    
    try:
        verificar_stock_y_notificar(app)
        AlertaController.guardar_fecha_global()
        AlertaController.guardar_fechas_productos(productos_bajos)
        flash('Alerta enviada y fechas actualizadas', 'success')
    except Exception as e:
        flash(f'Error al enviar alerta: {str(e)}', 'danger')
        current_app.logger.error(f"Error al enviar alerta: {str(e)}")
    
    return redirect(url_for('alertas.listar'))
