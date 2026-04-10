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

@consultas.route('/api/consultas', methods=['POST'])
def api_crear_consulta():
    """
    Crear consulta legal
    ---
    tags:
      - Consultas
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            cliente_id:
              type: integer
              example: 1
            asunto:
              type: string
              example: Incumplimiento de contrato de alquiler
            mensaje:
              type: string
              example: El arrendador no quiere devolver la garantía
            area:
              type: string
              example: Derecho Civil
    responses:
      201:
        description: Consulta creada correctamente
      400:
        description: Error en los datos
    """

    data = request.json

    if not data:
        return {"error": "No se enviaron datos"}, 400

    nueva_consulta = Consulta(
        cliente_id=data.get("cliente_id"),
        asunto=data.get("asunto"),
        mensaje=data.get("mensaje"),
        area=data.get("area"),
        estado="Pendiente"
    )

    db.session.add(nueva_consulta)
    db.session.commit()

    return {
        "mensaje": "Consulta creada correctamente",
        "id": nueva_consulta.id
    }, 201

@consultas.route('/api/consultas', methods=['GET'])
def api_listar_consultas():
    """
    Obtener todas las consultas
    ---
    tags:
      - Consultas
    responses:
      200:
        description: Lista de consultas
    """

    consultas = Consulta.query.all()

    resultado = []

    for c in consultas:
        resultado.append({
            "id": c.id,
            "cliente_id": c.cliente_id,
            "asunto": c.asunto,
            "mensaje": c.mensaje,
            "area": c.area,
            "estado": c.estado
        })

    return resultado

@consultas.route('/api/consultas/<int:id>', methods=['GET'])
def api_obtener_consulta(id):
    """
    Obtener consulta por ID
    ---
    tags:
      - Consultas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Consulta encontrada
      404:
        description: Consulta no encontrada
    """

    consulta = Consulta.query.get(id)

    if not consulta:
        return {"error": "Consulta no encontrada"}, 404

    return {
        "id": consulta.id,
        "cliente_id": consulta.cliente_id,
        "asunto": consulta.asunto,
        "mensaje": consulta.mensaje,
        "area": consulta.area,
        "estado": consulta.estado
    }

@consultas.route('/api/consultas/cliente/<int:cliente_id>', methods=['GET'])
def api_consultas_por_cliente(cliente_id):
    """
    Obtener consultas por cliente
    ---
    tags:
      - Consultas
    parameters:
      - name: cliente_id
        in: path
        type: integer
        required: true
        example: 1

    responses:
      200:
        description: Lista de consultas del cliente
    """

    consultas = Consulta.query.filter_by(cliente_id=cliente_id).all()

    resultado = []

    for c in consultas:

        resultado.append({
            "id": c.id,
            "asunto": c.asunto,
            "mensaje": c.mensaje,
            "area": c.area,
            "estado": c.estado
        })

    return resultado

@consultas.route('/api/consultas/abogado/<int:abogado_id>', methods=['GET'])
def api_consultas_por_abogado(abogado_id):
    """
    Obtener consultas por abogado
    ---
    tags:
      - Consultas
    parameters:
      - name: abogado_id
        in: path
        type: integer
        required: true
        example: 1

    responses:
      200:
        description: Lista de consultas asignadas al abogado
    """

    asignaciones = Asignacion.query.filter_by(abogado_id=abogado_id).all()

    clientes_ids = [a.cliente_id for a in asignaciones]

    consultas = Consulta.query.filter(
        Consulta.cliente_id.in_(clientes_ids)
    ).all()

    resultado = []

    for c in consultas:

        resultado.append({
            "id": c.id,
            "cliente_id": c.cliente_id,
            "asunto": c.asunto,
            "area": c.area,
            "estado": c.estado
        })

    return resultado

@consultas.route('/api/consultas/<int:id>/estado', methods=['PUT'])
def api_cambiar_estado_consulta(id):
    """
    Cambiar estado de consulta
    ---
    tags:
      - Consultas
    parameters:
      - name: id
        in: path
        type: integer
        required: true

      - name: body
        in: body
        required: true
        schema:
          properties:
            estado:
              type: string
              example: Respondida

    responses:
      200:
        description: Estado actualizado
      404:
        description: Consulta no encontrada
    """

    consulta = Consulta.query.get(id)

    if not consulta:
        return {"error": "Consulta no encontrada"}, 404

    data = request.json

    consulta.estado = data.get("estado")

    db.session.commit()

    return {
        "mensaje": "Estado actualizado",
        "estado": consulta.estado
    }