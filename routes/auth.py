from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Usuario, Cliente
from flask_login import login_user, logout_user, login_required
from models import Usuario
from werkzeug.security import generate_password_hash
from flask_login import current_user

auth = Blueprint('auth', __name__)

# REGISTRO CLIENTE
@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        dni = request.form['dni']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('El correo ya está registrado')
            return redirect(url_for('auth.registro'))

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            rol='cliente'
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        nuevo_cliente = Cliente(
            usuario_id=nuevo_usuario.id,
            dni=dni,
            telefono=telefono,
            direccion=direccion
        )

        db.session.add(nuevo_cliente)
        db.session.commit()

        flash('Registro exitoso')
        return redirect(url_for('auth.login'))

    return render_template('registro.html')


# LOGIN
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for('dashboard'))

        flash('Credenciales incorrectas')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


# LOGOUT
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))