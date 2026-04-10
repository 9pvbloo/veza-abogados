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


        if not email or not password:
            flash('Email y contraseña son obligatorios')
            return redirect(url_for('auth.registro'))

        # validar que al menos tenga DNI o RUC
        if not dni and not ruc:
            flash('Debe ingresar DNI o RUC')
            return redirect(url_for('auth.registro'))


        # =========================
        # CONSULTAR RENIEC
        # =========================

        nombre_completo = None

        # consultar DNI solo si existe
        if dni:
            datos_dni = consultar_dni(dni)

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

            # validar si el usuario está activo
            if not usuario.estado:
                flash('Su cuenta ha sido desactivada. Contacte al administrador.')
                return redirect(url_for('auth.login'))

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

# ==============================
# API REGISTRO
# ==============================

@auth.route('/api/registro', methods=['POST'])
def api_registro():
    """
    Registro de cliente
    ---
    tags:
      - Autenticación
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            nombre:
              type: string
              example: Juan Perez
            email:
              type: string
              example: cliente@gmail.com
            password:
              type: string
              example: 123456
            dni:
              type: string
              example: 12345678
            telefono:
              type: string
              example: 987654321
            direccion:
              type: string
              example: Av Siempre Viva 123
    responses:
      201:
        description: Usuario registrado correctamente
      400:
        description: Error en los datos
    """

    data = request.json

    if not data:
        return {"error": "No se enviaron datos"}, 400

    email = data.get("email")
    password = data.get("password")
    nombre = data.get("nombre")

    if not email or not password:
        return {"error": "Email y password obligatorios"}, 400

    usuario_existente = Usuario.query.filter_by(email=email).first()

    if usuario_existente:
        return {"error": "Correo ya registrado"}, 400


    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        rol="cliente"
    )

    nuevo_usuario.set_password(password)

    db.session.add(nuevo_usuario)
    db.session.commit()


    nuevo_cliente = Cliente(
        usuario_id=nuevo_usuario.id,
        dni=data.get("dni"),
        telefono=data.get("telefono"),
        direccion=data.get("direccion")
    )

    db.session.add(nuevo_cliente)
    db.session.commit()

    return {"mensaje": "Usuario registrado correctamente"}, 201



# ==============================
# API LOGIN
# ==============================

@auth.route('/api/login', methods=['POST'])
def api_login():
    """
    Login de usuario
    ---
    tags:
      - Autenticación
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
              example: cliente@gmail.com
            password:
              type: string
              example: 123456
    responses:
      200:
        description: Login exitoso
      401:
        description: Credenciales incorrectas
    """

    data = request.json

    if not data:
        return {"error": "No se enviaron datos"}, 400

    email = data.get("email")
    password = data.get("password")

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and usuario.check_password(password):

        return {
            "mensaje": "Login correcto",
            "usuario": usuario.email,
            "rol": usuario.rol
        }

    return {"error": "Credenciales incorrectas"}, 401