from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.sancion import Sancion

class SancionRepository:

    @staticmethod
    def crear(db: Session, id_usuario: int, id_prestamo: int, monto: Decimal, dias_retraso: int):
        nueva = Sancion(
            id_usuario=id_usuario,
            id_prestamo=id_prestamo,
            monto=monto,
            dias_retraso=dias_retraso,
            pagada=False
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva

    @staticmethod
    def obtener_por_id(db: Session, id_sancion: int):
        return db.query(Sancion).filter(Sancion.id_sancion == id_sancion).first()

    @staticmethod
    def listar_todas(db: Session):
        return db.query(Sancion).all()

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int):
        return db.query(Sancion).filter(Sancion.id_usuario == id_usuario).all()

    @staticmethod
    def listar_pendientes_por_usuario(db: Session, id_usuario: int):
        """Lista sanciones NO pagadas (para verificar si un usuario está bloqueado)."""
        return db.query(Sancion).filter(
            Sancion.id_usuario == id_usuario,
            Sancion.pagada == False
        ).all()

    @staticmethod
    def usuario_tiene_sancion_pendiente(db: Session, id_usuario: int) -> bool:
        """Devuelve True si el usuario tiene al menos una sanción sin pagar."""
        return db.query(Sancion).filter(
            Sancion.id_usuario == id_usuario,
            Sancion.pagada == False
        ).first() is not None

    @staticmethod
    def marcar_como_pagada(db: Session, id_sancion: int):
        sancion = db.query(Sancion).filter(Sancion.id_sancion == id_sancion).first()
        if sancion:
            sancion.pagada = True
            db.commit()
            db.refresh(sancion)
        return sancion