from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Consulta, Cliente

consultas = Blueprint('consultas', __name__)

@consultas.route('/nueva_consulta', methods=['GET', 'POST'])
@login_required
def nueva_consulta():
    if current_user.rol != "cliente":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        asunto = request.form['asunto']
        mensaje = request.form['mensaje']

        cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()

        nueva_consulta = Consulta(
            cliente_id=cliente.id,
            asunto=asunto,
            mensaje=mensaje,
            estado="Pendiente"
        )

        db.session.add(nueva_consulta)
        db.session.commit()

        flash("Consulta enviada correctamente")
        return redirect(url_for('dashboard'))

    return render_template('nueva_consulta.html')

@consultas.route('/mis_consultas')
@login_required
def mis_consultas():

    if current_user.rol != "cliente":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()

    consultas = Consulta.query.filter_by(cliente_id=cliente.id).all()

    return render_template("mis_consultas.html", consultas=consultas)