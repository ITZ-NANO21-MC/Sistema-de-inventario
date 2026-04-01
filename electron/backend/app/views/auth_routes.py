from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models import Usuario
from app.forms import LoginForm
from urllib.parse import urlparse
from app.services.audit import registrar_evento

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            registrar_evento('LOGIN_FALLIDO', f"Intento fallido para usuario='{form.username.data}' desde IP={request.remote_addr}", usuario=form.username.data)
            flash('Usuario o contraseña inválidos', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        registrar_evento('LOGIN_EXITOSO', f"Inicio de sesión exitoso desde IP={request.remote_addr}", usuario=user.username)
        
        # Redirigir a la página que el usuario intentaba visitar (si existe)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
            
        flash('Has iniciado sesión exitosamente.', 'success')
        return redirect(next_page)
        
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    registrar_evento('LOGOUT', f"Cierre de sesión desde IP={request.remote_addr}")
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))

