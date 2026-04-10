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

@documentos_bp.route('/api/documentos', methods=['POST'])
def api_subir_documento():
    """
    Subir documento legal
    ---
    tags:
      - Documentos
    parameters:
      - name: cliente_id
        in: formData
        type: integer
        required: true
        example: 1

      - name: archivo
        in: formData
        type: file
        required: true

    responses:
      201:
        description: Documento subido correctamente
      400:
        description: Error en el archivo
    """

    cliente_id = request.form.get("cliente_id")

    if "archivo" not in request.files:
        return {"error": "No se envió archivo"}, 400

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return {"error": "Archivo vacío"}, 400

    nuevo_documento = Documento(
        cliente_id=cliente_id,
        nombre_archivo=archivo.filename,
        archivo=archivo.read()
    )

    db.session.add(nuevo_documento)
    db.session.commit()

    return {
        "mensaje": "Documento subido correctamente",
        "id": nuevo_documento.id
    }, 201

@documentos_bp.route('/api/documentos', methods=['GET'])
def api_listar_documentos():
    """
    Obtener documentos
    ---
    tags:
      - Documentos
    responses:
      200:
        description: Lista de documentos
    """

    documentos = Documento.query.all()

    resultado = []

    for d in documentos:

        resultado.append({
            "id": d.id,
            "cliente_id": d.cliente_id,
            "nombre_archivo": d.nombre_archivo
        })

    return resultado

@documentos_bp.route('/api/documentos/<int:id>', methods=['GET'])
def api_obtener_documento(id):
    """
    Obtener documento por ID
    ---
    tags:
      - Documentos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        example: 1

    responses:
      200:
        description: Documento encontrado
      404:
        description: Documento no encontrado
    """

    documento = Documento.query.get(id)

    if not documento:
        return {"error": "Documento no encontrado"}, 404

    return {
        "id": documento.id,
        "cliente_id": documento.cliente_id,
        "nombre_archivo": documento.nombre_archivo
    }