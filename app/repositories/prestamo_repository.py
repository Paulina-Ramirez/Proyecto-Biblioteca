from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.models.prestamo import Prestamo

class PrestamoRepository:

    @staticmethod
    def crear(db: Session, id_usuario: int, id_libro: int, fecha_vencimiento: datetime, commit: bool = True):
        """
        Crea un préstamo. Con commit=False solo hace flush, para que el service
        pueda agrupar esta operación con otras en una sola transacción.
        """
        nuevo = Prestamo(
            id_usuario=id_usuario,
            id_libro=id_libro,
            fecha_vencimiento=fecha_vencimiento,
            estado="Activo"
        )
        db.add(nuevo)
        if commit:
            db.commit()
        else:
            db.flush()
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
    def obtener_fecha_vencimiento_mas_cercana(db: Session, id_libro: int, desde: Optional[datetime] = None):
        """
        Fecha de devolución más próxima de un libro: mínima fecha_vencimiento entre
        sus préstamos activos, sin devolver y con vencimiento >= 'desde' (por defecto, ahora).
        Devuelve None si no hay ninguno que cumpla.
        """
        desde = desde or datetime.now()
        return db.query(func.min(Prestamo.fecha_vencimiento)).filter(
            Prestamo.id_libro == id_libro,
            Prestamo.estado == "Activo",
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_vencimiento >= desde
        ).scalar()

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
    
    @staticmethod
    def actualizar_estado_devolucion(db: Session, id_prestamo: int, fecha_devolucion: datetime, commit: bool = True) -> int:
        """Marca el préstamo como Devuelto solo si aún no lo estaba.
        Devuelve filas afectadas (1 = ok, 0 = ya devuelto o inexistente)."""
        filas = db.query(Prestamo).filter(
            Prestamo.id_prestamo == id_prestamo,
            Prestamo.estado != "Devuelto"
        ).update(
            {Prestamo.estado: "Devuelto", Prestamo.fecha_devolucion: fecha_devolucion},
            synchronize_session=False
        )
        if commit:
            db.commit()
        return filas  

