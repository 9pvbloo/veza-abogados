from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Documento, Cliente
from datetime import datetime

documentos_bp = Blueprint('documentos', __name__)

@documentos_bp.route('/subir_documento', methods=['GET', 'POST'])
@login_required
def subir_documento():

    if current_user.rol != "cliente":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()

    if request.method == 'POST':
        archivo = request.files['archivo']

        if archivo.filename == '':
            flash("No seleccionaste archivo")
            return redirect(url_for('documentos.subir_documento'))

        nuevo_documento = Documento(
            cliente_id=cliente.id,
            nombre_archivo=archivo.filename,
            archivo=archivo.read(),
            fecha_subida=datetime.utcnow()
        )

        db.session.add(nuevo_documento)
        db.session.commit()

        flash("Documento subido correctamente")
        return redirect(url_for('dashboard'))

    return render_template('subir_documento.html')