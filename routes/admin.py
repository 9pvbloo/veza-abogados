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
from reportlab.platypus import Image
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

    abogados = Abogado.query.all()
    asignaciones = Asignacion.query.all()

    # dividir consultas
    consultas_pendientes = Consulta.query.filter_by(
        estado="Pendiente"
    ).order_by(Consulta.fecha_creacion.desc()).all()

    consultas_asignadas = Consulta.query.filter(
        Consulta.estado != "Pendiente"
    ).order_by(Consulta.fecha_creacion.desc()).all()


    if request.method == 'POST':

        cliente_id = request.form['cliente_id']
        abogado_id = request.form['abogado_id']

        # evitar duplicados
        asignacion_existente = Asignacion.query.filter_by(
            cliente_id=cliente_id,
            abogado_id=abogado_id
        ).first()

        if not asignacion_existente:

            nueva_asignacion = Asignacion(
                cliente_id=cliente_id,
                abogado_id=abogado_id
            )

            db.session.add(nueva_asignacion)


        # actualizar consultas pendientes del cliente
        consultas_cliente = Consulta.query.filter_by(
            cliente_id=cliente_id,
            estado="Pendiente"
        ).all()

        for consulta in consultas_cliente:

            consulta.abogado_id = abogado_id
            consulta.estado = "Asignado"


        db.session.commit()

        flash("Consulta asignada correctamente")

        return redirect(url_for('admin.asignar_cliente'))


    return render_template(
        'asignar_cliente.html',

        abogados=abogados,
        asignaciones=asignaciones,

        consultas_pendientes=consultas_pendientes,
        consultas_asignadas=consultas_asignadas
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

    # ===== LOGO =====
    logo_path = "static/img/logo_veza.jpg"  
    logo = Image(logo_path, width=80, height=80)

    # ===== HEADER =====
    header = [
        [logo, Paragraph("<b>VEZA ABOGADOS</b><br/>Reporte Administrativo", styles['Title'])]
    ]

    header_table = Table(header, colWidths=[90, 400])
    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles['Normal']
    ))

    elements.append(Spacer(1, 0.4 * inch))

    # ===== RESUMEN =====
    elements.append(Paragraph("<b>Resumen General</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    total_usuarios = Usuario.query.count()
    total_clientes = Cliente.query.count()
    total_abogados = Abogado.query.count()
    total_consultas = Consulta.query.count()
    activos = Usuario.query.filter_by(estado=True).count()
    inactivos = Usuario.query.filter_by(estado=False).count()

    data = [
        ["Concepto", "Cantidad"],
        ["Total Usuarios", total_usuarios],
        ["Total Clientes", total_clientes],
        ["Total Abogados", total_abogados],
        ["Total Consultas", total_consultas],
        ["Usuarios Activos", activos],
        ["Usuarios Inactivos", inactivos],
    ]

    table = Table(data, colWidths=[300, 100])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 0.5 * inch))

    # ===== LISTA DE ABOGADOS =====
    elements.append(Paragraph("<b>Listado de Abogados</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    abogados = Abogado.query.all()

    abogados_data = [["Nombre", "Email"]]

    for ab in abogados:
        abogados_data.append([
            ab.usuario.nombre,
            ab.usuario.email
        ])

    tabla_abogados = Table(abogados_data, colWidths=[200, 200])

    tabla_abogados.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(tabla_abogados)

    elements.append(Spacer(1, 0.5 * inch))

    # ===== FOOTER =====
    elements.append(Paragraph(
        "Veza Abogados © 2026 - Sistema de Gestión Legal",
        styles['Normal']
    ))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_admin.pdf",
        mimetype='application/pdf'
    )

@admin.route('/dashboard_admin')
@login_required
def dashboard_admin():

    if current_user.rol != "admin":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    # ===== GRAFICO 1 =====
    consultas_estado = db.session.query(
        Consulta.estado,
        db.func.count(Consulta.id)
    ).group_by(Consulta.estado).all()

    estado_labels = [c[0] for c in consultas_estado] if consultas_estado else ["Sin datos"]
    estado_data = [c[1] for c in consultas_estado] if consultas_estado else [0]


    # ===== GRAFICO 2 =====
    consultas_area = db.session.query(
        Consulta.area,
        db.func.count(Consulta.id)
    ).group_by(Consulta.area).all()

    area_labels = [c[0] for c in consultas_area] if consultas_area else ["Sin datos"]
    area_data = [c[1] for c in consultas_area] if consultas_area else [0]


    # ===== GRAFICO 3 (compatible con Railway) =====
    consultas_mes = db.session.query(
        Consulta.fecha_creacion,
        db.func.count(Consulta.id)
    ).group_by(Consulta.fecha_creacion).all()

    mes_labels = [str(c[0])[:7] for c in consultas_mes] if consultas_mes else ["Sin datos"]
    mes_data = [c[1] for c in consultas_mes] if consultas_mes else [0]


    return render_template(
        "dashboard_admin.html",

        estado_labels=estado_labels,
        estado_data=estado_data,

        area_labels=area_labels,
        area_data=area_data,

        mes_labels=mes_labels,
        mes_data=mes_data
    )