from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Abogado, Asignacion, Consulta, Cliente
from flask import request
from flask import send_file
import io
from models import Documento
from sqlalchemy import text
from extensions import db

abogado_bp = Blueprint('abogado', __name__, url_prefix='/abogado')

@abogado_bp.route('/mis_consultas')
@login_required
def mis_consultas():

    if current_user.rol != "abogado":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    abogado = Abogado.query.filter_by(usuario_id=current_user.id).first()

    asignaciones = Asignacion.query.filter_by(abogado_id=abogado.id).all()

    clientes_ids = [a.cliente_id for a in asignaciones]

    if not clientes_ids:
        consultas = []
    else:
        consultas = db.session.query(Consulta, Cliente)\
            .join(Cliente, Consulta.cliente_id == Cliente.id)\
            .filter(Consulta.cliente_id.in_(clientes_ids)).all()

    pendientes = sum(
        1 for consulta, cliente in consultas
        if consulta.estado and consulta.estado.lower() == "pendiente"
    )

    return render_template(
        "mis_consultas.html",
        consultas=consultas,
        pendientes=pendientes
    )

@abogado_bp.route('/responder/<int:consulta_id>', methods=['GET', 'POST'])
@login_required
def responder_consulta(consulta_id):

    if current_user.rol != "abogado":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    consulta = Consulta.query.get_or_404(consulta_id)

    if request.method == 'POST':
        respuesta = request.form['respuesta']
        consulta.respuesta = respuesta
        connection = db.engine.raw_connection()
        cursor = connection.cursor()

        cursor.callproc("sp_cambiar_estado_consulta", [consulta.id, "Respondida"])

        connection.commit()
        cursor.close()
        connection.close()

        db.session.commit()

        flash("Consulta respondida correctamente")
        return redirect(url_for('abogado.mis_consultas'))

    return render_template('responder_consulta.html', consulta=consulta)

@abogado_bp.route('/mis_documentos')
@login_required
def mis_documentos():

    if current_user.rol != "abogado":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    abogado = Abogado.query.filter_by(usuario_id=current_user.id).first()

    asignaciones = Asignacion.query.filter_by(abogado_id=abogado.id).all()
    clientes_ids = [a.cliente_id for a in asignaciones]

    documentos = db.session.query(Documento, Cliente)\
        .join(Cliente, Documento.cliente_id == Cliente.id)\
        .filter(Documento.cliente_id.in_(clientes_ids)).all()

    return render_template('mis_documentos.html', documentos=documentos)

@abogado_bp.route('/descargar_documento/<int:documento_id>')
@login_required
def descargar_documento(documento_id):

    if current_user.rol != "abogado":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    documento = Documento.query.get_or_404(documento_id)

    return send_file(
        io.BytesIO(documento.archivo),
        download_name=documento.nombre_archivo,
        as_attachment=True
    )