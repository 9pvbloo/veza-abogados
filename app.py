from flask import Flask, render_template
from config import Config
from extensions import db, login_manager
from sqlalchemy import text
import models

# Blueprints
from routes.auth import auth
from routes.consultas import consultas
from routes.admin import admin
from routes.abogado import abogado_bp
from routes.cliente import cliente_bp
from routes.documentos import documentos_bp

# Modelos
from models import Usuario, Cliente, Abogado, Consulta, Documento, Asignacion
from flask_login import login_required, current_user

app = Flask(__name__)
app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registrar blueprints
app.register_blueprint(auth)
app.register_blueprint(consultas)
app.register_blueprint(admin)
app.register_blueprint(abogado_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(documentos_bp)

@app.context_processor
def contador_consultas_pendientes():

    from flask_login import current_user
    from models import Abogado, Consulta

    if current_user.is_authenticated and current_user.rol == "abogado":

        abogado = Abogado.query.filter_by(usuario_id=current_user.id).first()

        if abogado:
            pendientes = Consulta.query.filter_by(
                abogado_id=abogado.id,
                estado="Pendiente"
            ).count()
        else:
            pendientes = 0

    else:
        pendientes = 0

    return dict(pendientes=pendientes)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/areas")
def areas():
    return render_template("areas.html")

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/derecho-penal")
def derecho_penal():
    return render_template("derecho_penal.html")

@app.route("/derecho-civil")
def derecho_civil():
    return render_template("derecho_civil.html")

@app.route("/derecho-ambiental")
def derecho_ambiental():
    return render_template("derecho_ambiental.html")

@app.route("/dashboard")
@login_required
def dashboard():

    # ================= CLIENTE =================
    if current_user.rol == "cliente":

        cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()

        total_consultas = Consulta.query.filter_by(cliente_id=cliente.id).count()
        pendientes = Consulta.query.filter_by(cliente_id=cliente.id, estado="Pendiente").count()
        respondidas = Consulta.query.filter_by(cliente_id=cliente.id, estado="Respondida").count()
        total_documentos = Documento.query.filter_by(cliente_id=cliente.id).count()

        return render_template(
            "dashboard_cliente.html",
            total_consultas=total_consultas,
            pendientes=pendientes,
            respondidas=respondidas,
            total_documentos=total_documentos
        )

    # ================= ABOGADO =================
    elif current_user.rol == "abogado":

        abogado = Abogado.query.filter_by(usuario_id=current_user.id).first()

        # clientes asignados al abogado
        asignaciones = Asignacion.query.filter_by(abogado_id=abogado.id).all()
        clientes_ids = [a.cliente_id for a in asignaciones]

        if clientes_ids:
            total_consultas = Consulta.query.filter(Consulta.cliente_id.in_(clientes_ids)).count()

            pendientes = Consulta.query.filter(
                Consulta.cliente_id.in_(clientes_ids),
                Consulta.estado == "Pendiente"
            ).count()

            respondidas = Consulta.query.filter(
                Consulta.cliente_id.in_(clientes_ids),
                Consulta.estado == "Respondida"
            ).count()
        else:
            total_consultas = 0
            pendientes = 0
            respondidas = 0

        total_documentos = Documento.query.filter(Documento.cliente_id.in_(clientes_ids)).count()

        return render_template(
            "dashboard_abogado.html",
            total_consultas=total_consultas,
            pendientes=pendientes,
            respondidas=respondidas,
            total_documentos=total_documentos
        )

    # ================= ADMIN =================
    elif current_user.rol == "admin":

        connection = db.engine.raw_connection()
        cursor = connection.cursor()

        cursor.callproc("sp_dashboard_admin")

        for result in cursor.stored_results():
            data = result.fetchone()

        cursor.close()
        connection.close()

        total_usuarios = data[0]
        total_clientes = data[1]
        total_abogados = data[2]
        total_consultas = data[3]
        activos = data[4]
        inactivos = data[5]
        pendientes = data[6]
        respondidas = data[7]

        return render_template(
            "dashboard_admin.html",
            total_usuarios=total_usuarios,
            total_clientes=total_clientes,
            total_abogados=total_abogados,
            total_consultas=total_consultas,
            activos=activos,
            inactivos=inactivos,
            pendientes=pendientes,
            respondidas=respondidas
        )

    else:
        return "Rol no reconocido"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)