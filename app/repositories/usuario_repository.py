from sqlalchemy.orm import Session
from app.models.usuario import Usuario

class UsuarioRepository:

    @staticmethod
    def crear(db: Session, nombre: str, email: str, password_hash: str, rol: str):
        nuevo = Usuario(
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            rol=rol
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo

    @staticmethod
    def obtener_por_id(db: Session, id_usuario: int):
        return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    @staticmethod
    def obtener_por_email(db: Session, email: str):
        return db.query(Usuario).filter(Usuario.email == email).first()

    @staticmethod
    def listar_todos(db: Session):
        return db.query(Usuario).all()

    @staticmethod
    def listar_por_rol(db: Session, rol: str):
        return db.query(Usuario).filter(Usuario.rol == rol).all()

    @staticmethod
    def actualizar(db: Session, id_usuario: int, **kwargs):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if usuario:
            for key, value in kwargs.items():
                setattr(usuario, key, value)
            db.commit()
            db.refresh(usuario)
        return usuario

    @staticmethod
    def eliminar(db: Session, id_usuario: int):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if usuario:
            db.delete(usuario)
            db.commit()
        return usuario