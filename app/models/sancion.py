from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from app.config.database import Base

class Sancion(Base):
    __tablename__ = "Sanciones"

    id_sancion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    id_prestamo = Column(Integer, ForeignKey("Prestamos.id_prestamo"), nullable=False)
    monto = Column(DECIMAL(10, 2), default=0)
    dias_retraso = Column(Integer, default=0)
    pagada = Column(Boolean, default=False)
    fecha_sancion = Column(DateTime, server_default=func.now())