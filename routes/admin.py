from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Usuario, Abogado, Cliente, Consulta  
from models import Cliente, Asignacion
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from datetime import datetime
import io

admin = Blueprint('admin', __name__)

@admin.route('/crear_abogado', methods=['GET', 'POST'])
@login_required
def crear_abogado():
    if current_user.rol != "admin":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        especialidad = request.form['especialidad']

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("El correo ya está registrado")
            return redirect(url_for('admin.crear_abogado'))

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            rol='abogado'
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        nuevo_abogado = Abogado(
            usuario_id=nuevo_usuario.id,
            especialidad=especialidad
        )

        db.session.add(nuevo_abogado)
        db.session.commit()

        flash("Abogado creado correctamente")
        return redirect(url_for('dashboard'))
    

    return render_template('crear_abogado.html')

@admin.route('/asignar_cliente', methods=['GET', 'POST'])
@login_required
def asignar_cliente():

    if current_user.rol != "admin":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    clientes = Cliente.query.all()
    abogados = Abogado.query.all()
    asignaciones = Asignacion.query.all()

    if request.method == 'POST':

        cliente_id = request.form['cliente_id']
        abogado_id = request.form['abogado_id']

        asignacion_existente = Asignacion.query.filter_by(
            cliente_id=cliente_id,
            abogado_id=abogado_id
        ).first()

        if asignacion_existente:
            flash("Ya está asignado")
            return redirect(url_for('admin.asignar_cliente'))

        nueva_asignacion = Asignacion(
            cliente_id=cliente_id,
            abogado_id=abogado_id
        )

        db.session.add(nueva_asignacion)
        db.session.commit()

        # asignar abogado a consultas existentes del cliente
        consultas = Consulta.query.filter_by(cliente_id=cliente_id).all()

        for consulta in consultas:
            consulta.abogado_id = abogado_id

        db.session.commit()

        flash("Cliente asignado correctamente")

        return redirect(url_for('admin.asignar_cliente'))

    return render_template(
        'asignar_cliente.html',
        clientes=clientes,
        abogados=abogados,
        asignaciones=asignaciones
    )

@admin.route('/usuarios')
@login_required
def listar_usuarios():

    if current_user.rol != "admin":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    usuarios = Usuario.query.all()

    return render_template('listar_usuarios.html', usuarios=usuarios)

@admin.route('/desactivar_usuario/<int:user_id>')
@login_required
def desactivar_usuario(user_id):

    if current_user.rol != "admin":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    usuario = Usuario.query.get_or_404(user_id)
    usuario.estado = False
    db.session.commit()

    flash("Usuario desactivado correctamente")
    return redirect(url_for('admin.listar_usuarios'))


@admin.route('/activar_usuario/<int:user_id>')
@login_required
def activar_usuario(user_id):

    if current_user.rol != "admin":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    usuario = Usuario.query.get_or_404(user_id)
    usuario.estado = True
    db.session.commit()

    flash("Usuario activado correctamente")
    return redirect(url_for('admin.listar_usuarios'))

@admin.route('/reporte_pdf')
@login_required
def reporte_pdf():

    if current_user.rol != "admin":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("REPORTE ADMINISTRATIVO - VEZA ABOGADOS", styles['Heading1']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # Datos
    total_usuarios = Usuario.query.count()
    total_clientes = Cliente.query.count()
    total_abogados = Abogado.query.count()
    total_consultas = Consulta.query.count()
    activos = Usuario.query.filter_by(estado=True).count()
    inactivos = Usuario.query.filter_by(estado=False).count()

    data = [
        ["Total Usuarios", total_usuarios],
        ["Total Clientes", total_clientes],
        ["Total Abogados", total_abogados],
        ["Total Consultas", total_consultas],
        ["Usuarios Activos", activos],
        ["Usuarios Inactivos", inactivos],
    ]

    table = Table(data, colWidths=[250, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_admin.pdf",
        mimetype='application/pdf'
    )