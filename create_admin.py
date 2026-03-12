from app import app
from extensions import db
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    admin_existente = Usuario.query.filter_by(email="admin@veza.com").first()

    if not admin_existente:
        nuevo_admin = Usuario(
            nombre="Administrador",
            email="admin@veza.com",
            rol="admin"
        )
        nuevo_admin.set_password("Admin123")

        db.session.add(nuevo_admin)
        db.session.commit()

        print("Administrador creado correctamente ✅")
    else:
        print("El administrador ya existe ⚠️")