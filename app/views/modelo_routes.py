from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import ModeloTelefono
from app.forms import ModeloForm
from app import db

from flask_login import login_required

modelo_bp = Blueprint('modelo', __name__, template_folder='../templates/modelo')

@modelo_bp.before_request
@login_required
def require_login():
    pass

@modelo_bp.route('/')
def listar():
    busqueda = request.args.get('busqueda', '').strip()
    marca = request.args.get('marca', '').strip()
    
    query = ModeloTelefono.query
    
    if busqueda:
        query = query.filter(ModeloTelefono.nombre.ilike(f'%{busqueda}%'))
    if marca:
        query = query.filter(ModeloTelefono.marca == marca)
    
    modelos = query.order_by(ModeloTelefono.nombre).all()
    
    # Obtener marcas únicas para el filtro dinámico
    marcas = db.session.query(ModeloTelefono.marca).filter(
        ModeloTelefono.marca.isnot(None), ModeloTelefono.marca != ''
    ).distinct().order_by(ModeloTelefono.marca).all()
    marcas = [m[0] for m in marcas]
    
    return render_template('modelo/listar.html', modelos=modelos, marcas=marcas)


@modelo_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    form = ModeloForm()
    if form.validate_on_submit():
        modelo = ModeloTelefono(nombre=form.nombre.data, marca=form.marca.data)
        db.session.add(modelo)
        db.session.commit()
        flash('Modelo creado exitosamente', 'success')
        return redirect(url_for('modelo.listar'))
    return render_template('modelo/crear.html', form=form)


@modelo_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    modelo = ModeloTelefono.query.get_or_404(id)
    form = ModeloForm(obj=modelo)
    if form.validate_on_submit():
        modelo.nombre = form.nombre.data
        modelo.marca = form.marca.data
        db.session.commit()
        flash('Modelo actualizado', 'success')
        return redirect(url_for('modelo.listar'))
    return render_template('modelo/editar.html', form=form, modelo=modelo)


@modelo_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    modelo = ModeloTelefono.query.get_or_404(id)
    db.session.delete(modelo)
    db.session.commit()
    flash('Modelo eliminado', 'success')
    return redirect(url_for('modelo.listar'))