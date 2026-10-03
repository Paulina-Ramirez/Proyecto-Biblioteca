from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.config.database import Base

class Prestamo(Base):
    __tablename__ = "Prestamos"

    id_prestamo = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    id_libro = Column(Integer, ForeignKey("Libros.id_libro"), nullable=False)
    fecha_prestamo = Column(DateTime, server_default=func.now())
    fecha_vencimiento = Column(DateTime, nullable=False)
    fecha_devolucion = Column(DateTime, nullable=True)
    estado = Column(String(20), default="Activo")