from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app.controllers.producto import ProductoController
from app.forms import ProductoForm
from app.services.alertas import verificar_stock_y_notificar, generar_informe_general
from config import Config

producto_bp = Blueprint('producto', __name__, template_folder='../templates/producto')

def get_tasa_cambio():
    return Config.TASA_CAMBIO_USD_BS

@producto_bp.route('/')
def listar():
    productos = ProductoController.obtener_todos()
    return render_template('listar.html', productos=productos)

@producto_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    form = ProductoForm()
    if form.validate_on_submit():
        data = {
            'nombre': form.nombre.data,
            'descripcion': form.descripcion.data,
            'categoria': form.categoria.data,
            'cantidad_stock': form.cantidad_stock.data,
            'stock_minimo': form.stock_minimo.data,
            'proveedor': form.proveedor.data,
            'precio_mayor_bs': form.precio_mayor_bs.data or 0,
            'precio_mayor_usd': form.precio_mayor_usd.data or 0,
            'precio_detal_bs': form.precio_detal_bs.data or 0,
            'precio_detal_usd': form.precio_detal_usd.data or 0
        }
        modelos_ids = form.modelos_compatibles.data if form.categoria.data == 'pantalla' else []
        ProductoController.crear(data, modelos_ids)
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('producto.listar'))
    tasa = get_tasa_cambio()
    return render_template('crear.html', form=form, tasa_cambio=tasa)

@producto_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    producto = ProductoController.obtener_por_id(id)
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('producto.listar'))

    form = ProductoForm(obj=producto)
    if request.method == 'GET':
        # Precargar modelos compatibles
        modelos_ids = [m.id for m in producto.modelos_compatibles]
        form.modelos_compatibles.data = modelos_ids
        print("=== CARGA INICIAL DEL FORMULARIO ===")
        print("Producto ID:", id)
        print("Modelos compatibles precargados (IDs):", modelos_ids)

    if form.validate_on_submit():
        print("=== FORMULARIO VÁLIDO ===")
        print("Categoría:", form.categoria.data)
        print("Modelos compatibles (enviados):", form.modelos_compatibles.data)
        data = {
            'nombre': form.nombre.data,
            'descripcion': form.descripcion.data,
            'categoria': form.categoria.data,
            'cantidad_stock': form.cantidad_stock.data,
            'stock_minimo': form.stock_minimo.data,
            'proveedor': form.proveedor.data,
            'precio_mayor_bs': form.precio_mayor_bs.data or 0,
            'precio_mayor_usd': form.precio_mayor_usd.data or 0,
            'precio_detal_bs': form.precio_detal_bs.data or 0,
            'precio_detal_usd': form.precio_detal_usd.data or 0
        }
        modelos_ids = form.modelos_compatibles.data if form.categoria.data == 'pantalla' else []
        ProductoController.actualizar(id, data, modelos_ids)
        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('producto.listar'))
    else:
        if form.errors:
            print("=== ERRORES EN FORMULARIO ===")
            print(form.errors)

    tasa = get_tasa_cambio()
    return render_template('producto/editar.html', form=form, producto=producto, tasa_cambio=tasa)

@producto_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    if ProductoController.eliminar(id):
        flash('Producto eliminado', 'success')
    else:
        flash('Error al eliminar el producto', 'danger')
    return redirect(url_for('producto.listar'))

@producto_bp.route('/enviar-alerta-manual')
def enviar_alerta_manual():
    """Envía manualmente una alerta de stock bajo por email."""
    try:
        verificar_stock_y_notificar(current_app._get_current_object())
        flash('Alerta de stock bajo enviada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al enviar la alerta: {str(e)}', 'danger')
        current_app.logger.error(f"Error en envío manual de alerta: {str(e)}")
    return redirect(url_for('producto.listar'))

@producto_bp.route('/enviar-informe-manual')
def enviar_informe_manual():
    """Envía manualmente el informe general de inventario por email."""
    try:
        generar_informe_general(current_app._get_current_object())
        flash('Informe general enviado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al enviar el informe: {str(e)}', 'danger')
        current_app.logger.error(f"Error en envío manual de informe: {str(e)}")
    return redirect(url_for('producto.listar'))