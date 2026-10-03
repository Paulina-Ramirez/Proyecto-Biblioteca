from sqlalchemy.orm import Session
from datetime import datetime
from app.models.prestamo import Prestamo

class PrestamoRepository:

    @staticmethod
    def crear(db: Session, id_usuario: int, id_libro: int, fecha_vencimiento: datetime):
        nuevo = Prestamo(
            id_usuario=id_usuario,
            id_libro=id_libro,
            fecha_vencimiento=fecha_vencimiento,
            estado="Activo"
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo

    @staticmethod
    def obtener_por_id(db: Session, id_prestamo: int):
        return db.query(Prestamo).filter(Prestamo.id_prestamo == id_prestamo).first()

    @staticmethod
    def listar_todos(db: Session):
        return db.query(Prestamo).all()

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int):
        return db.query(Prestamo).filter(Prestamo.id_usuario == id_usuario).all()

    @staticmethod
    def contar_activos_por_usuario(db: Session, id_usuario: int):
        """Cuenta cuántos préstamos activos tiene un usuario (útil para RF3)."""
        return db.query(Prestamo).filter(
            Prestamo.id_usuario == id_usuario,
            Prestamo.estado == "Activo"
        ).count()

    @staticmethod
    def listar_activos(db: Session):
        return db.query(Prestamo).filter(Prestamo.estado == "Activo").all()

    @staticmethod
    def registrar_devolucion(db: Session, id_prestamo: int, fecha_devolucion: datetime):
        prestamo = db.query(Prestamo).filter(Prestamo.id_prestamo == id_prestamo).first()
        if prestamo:
            prestamo.fecha_devolucion = fecha_devolucion
            prestamo.estado = "Devuelto"
            db.commit()
            db.refresh(prestamo)
        return prestamo

    @staticmethod
    def actualizar_estado(db: Session, id_prestamo: int, nuevo_estado: str):
        prestamo = db.query(Prestamo).filter(Prestamo.id_prestamo == id_prestamo).first()
        if prestamo:
            prestamo.estado = nuevo_estado
            db.commit()
            db.refresh(prestamo)
        return prestamo