from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # cliente, abogado, admin
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = db.relationship('Usuario')

    dni = db.Column(db.String(15))
    ruc = db.Column(db.String(11))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))


class Abogado(db.Model):
    __tablename__ = 'abogados'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = db.relationship('Usuario')

    especialidad = db.Column(db.String(100))


class Asignacion(db.Model):
    __tablename__ = 'asignaciones'

    id = db.Column(db.Integer, primary_key=True)

    abogado_id = db.Column(db.Integer, db.ForeignKey('abogados.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

    abogado = db.relationship('Abogado')
    cliente = db.relationship('Cliente')


class Consulta(db.Model):

    __tablename__ = 'consultas'

    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey('clientes.id'),
        nullable=False
    )

    abogado_id = db.Column(
        db.Integer,
        db.ForeignKey('abogados.id'),
        nullable=True
    )

    area = db.Column(db.String(100), nullable=False)

    asunto = db.Column(db.String(200), nullable=False)

    mensaje = db.Column(db.Text, nullable=False)

    respuesta = db.Column(db.Text)

    estado = db.Column(db.String(50), default="Pendiente")

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    abogado = db.relationship('Abogado', backref='consultas')

    cliente = db.relationship(
        'Cliente',
        backref='consultas_cliente'
    )


class Documento(db.Model):
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    abogado_id = db.Column(db.Integer, db.ForeignKey('abogados.id'), nullable=True)
    nombre_archivo = db.Column(db.String(255))
    archivo = db.Column(db.LargeBinary)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

class Mensaje(db.Model):
    __tablename__ = 'mensajes'

    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario')

class Contacto(db.Model):

    __tablename__ = "contactos"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100))

    email = db.Column(db.String(120))

    telefono = db.Column(db.String(20))

    mensaje = db.Column(db.Text)

    fecha = db.Column(db.DateTime, default=datetime.utcnow)