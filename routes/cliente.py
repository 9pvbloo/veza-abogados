from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Cliente, Consulta

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/mis_consultas_cliente')
@login_required
def mis_consultas_cliente():

    if current_user.rol != "cliente":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()

    consultas = Consulta.query.filter_by(cliente_id=cliente.id).all()

    return render_template('mis_consultas_cliente.html', consultas=consultas)