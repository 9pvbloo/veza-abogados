from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Usuario, Cliente
from flask_login import login_user, logout_user, login_required
from models import Usuario
from werkzeug.security import generate_password_hash
from flask_login import current_user
from api_peru import consultar_dni
from api_peru import consultar_dni, consultar_ruc

auth = Blueprint('auth', __name__)

# REGISTRO CLIENTE
from api_peru import consultar_dni


@auth.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':

        nombre_manual = request.form.get('nombre')
        email = request.form['email']
        password = request.form['password']
        dni = request.form['dni']
        ruc = request.form.get('ruc')
        telefono = request.form['telefono']
        direccion = request.form['direccion']


        if not email or not password or not dni:

            flash('Todos los campos obligatorios')

            return redirect(url_for('auth.registro'))


        # =========================
        # CONSULTAR RENIEC
        # =========================

        datos_dni = consultar_dni(dni)

        nombre_completo = None


        if datos_dni and datos_dni.get("success") != False:

            nombre = datos_dni.get("nombres")
            apellido_paterno = datos_dni.get("apellidoPaterno")
            apellido_materno = datos_dni.get("apellidoMaterno")

            nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}"


        # =========================
        # CONSULTAR SUNAT (RUC)
        # =========================

        if ruc:

            datos_ruc = consultar_ruc(ruc)

            if datos_ruc and datos_ruc.get("razonSocial"):

                nombre_completo = datos_ruc.get("razonSocial")

                flash("Empresa validada con SUNAT")

            else:

                flash("No se pudo validar el RUC")


        # =========================
        # FALLBACK SI API NO RESPONDE
        # =========================

        if not nombre_completo:

            if nombre_manual:

                nombre_completo = nombre_manual

                flash("Nombre registrado manualmente")

            else:

                flash("Debe ingresar nombre si DNI no es validado")

                return redirect(url_for('auth.registro'))


        # =========================
        # VALIDAR EMAIL
        # =========================

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:

            flash('El correo ya está registrado')

            return redirect(url_for('auth.registro'))


        # =========================
        # CREAR USUARIO
        # =========================

        nuevo_usuario = Usuario(

            nombre=nombre_completo,
            email=email,
            rol='cliente'

        )

        # contraseña protegida por firebase
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)

        db.session.commit()


        # =========================
        # CREAR CLIENTE
        # =========================

        nuevo_cliente = Cliente(

            usuario_id=nuevo_usuario.id,
            dni=dni,
            ruc=ruc,
            telefono=telefono,
            direccion=direccion

        )

        db.session.add(nuevo_cliente)

        db.session.commit()


        login_user(nuevo_usuario)

        flash('Registro exitoso')

        return redirect(url_for('dashboard'))


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

