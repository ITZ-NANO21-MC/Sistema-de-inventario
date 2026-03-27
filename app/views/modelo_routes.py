from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import ModeloTelefono
from app.forms import ModeloForm
from app import db

modelo_bp = Blueprint('modelo', __name__, template_folder='../templates/modelo')

@modelo_bp.route('/')
def listar():
    modelos = ModeloTelefono.query.order_by(ModeloTelefono.nombre).all()
    return render_template('modelo/listar.html', modelos=modelos)


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