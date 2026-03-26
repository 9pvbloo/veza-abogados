from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Consulta, Cliente, Abogado, Asignacion, Mensaje

consultas = Blueprint('consultas', __name__)


# =========================
# CREAR CONSULTA (CLIENTE)
# =========================

@consultas.route('/nueva_consulta', methods=['GET', 'POST'])
@login_required
def nueva_consulta():

    if current_user.rol != "cliente":
        flash("Acceso no autorizado")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        area = request.form['area']
        asunto = request.form['asunto']
        mensaje = request.form['mensaje']

        cliente = Cliente.query.filter_by(
            usuario_id=current_user.id
        ).first()


        nueva_consulta = Consulta(
            cliente_id=cliente.id,
            area=area,
            asunto=asunto,
            mensaje=mensaje,
            estado="Pendiente"
        )

        db.session.add(nueva_consulta)
        db.session.commit()


        # primer mensaje del chat
        primer_mensaje = Mensaje(
            consulta_id=nueva_consulta.id,
            usuario_id=current_user.id,
            contenido=mensaje
        )

        db.session.add(primer_mensaje)
        db.session.commit()


        flash("Consulta enviada correctamente")

        return redirect(
            url_for(
                'consultas.ver_consulta',
                id=nueva_consulta.id
            )
        )


    return render_template('nueva_consulta.html')



# =========================
# CLIENTE VE SUS CONSULTAS
# =========================

@consultas.route('/mis_consultas')
@login_required
def mis_consultas():

    if current_user.rol != "cliente":

        flash("Acceso no autorizado")

        return redirect(url_for('dashboard'))


    cliente = Cliente.query.filter_by(
        usuario_id=current_user.id
    ).first()


    consultas = Consulta.query.filter_by(
        cliente_id=cliente.id
    ).order_by(
        Consulta.fecha_creacion.desc()
    ).all()


    return render_template(
        "mis_consultas.html",
        consultas=consultas
    )



# =========================
# VER CONSULTA / CHAT
# =========================

@consultas.route('/consulta/<int:id>', methods=['GET', 'POST'])
@login_required
def ver_consulta(id):

    consulta = Consulta.query.get_or_404(id)


    # =========================
    # SEGURIDAD
    # =========================

    # CLIENTE solo puede ver su consulta
    if current_user.rol == "cliente":

        cliente = Cliente.query.filter_by(
            usuario_id=current_user.id
        ).first()


        if consulta.cliente_id != cliente.id:

            flash("No tienes acceso a esta consulta")

            return redirect(
                url_for(
                    "consultas.mis_consultas"
                )
            )



    # ABOGADO solo puede ver consultas asignadas a él
    elif current_user.rol == "abogado":

        abogado = Abogado.query.filter_by(
            usuario_id=current_user.id
        ).first()


        if consulta.abogado_id != abogado.id:

            flash("No tienes acceso a esta consulta")

            return redirect(
                url_for(
                    "dashboard"
                )
            )



    # ADMIN puede ver todo
    elif current_user.rol == "admin":

        pass



    # =========================
    # GUARDAR MENSAJE
    # =========================

    if request.method == 'POST':

        texto = request.form.get('mensaje')

        if texto:

            nuevo = Mensaje(

                consulta_id=consulta.id,

                usuario_id=current_user.id,

                contenido=texto

            )


            db.session.add(nuevo)

            db.session.commit()


        return redirect(
            url_for(
                'consultas.ver_consulta',
                id=id
            )
        )



    # =========================
    # MOSTRAR MENSAJES
    # =========================

    mensajes = Mensaje.query.filter_by(
        consulta_id=id
    ).order_by(
        Mensaje.fecha.asc()
    ).all()



    return render_template(

        'chat_consulta.html',

        consulta=consulta,

        mensajes=mensajes

    )