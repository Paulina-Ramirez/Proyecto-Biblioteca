from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.config.database import Base

class Libro(Base):
    __tablename__ = "Libros"

    id_libro = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(20), unique=True, nullable=False)
    titulo = Column(String(200), nullable=False)
    autor = Column(String(150), nullable=False)
    categoria = Column(String(80))
    stock_total = Column(Integer, nullable=False, default=0)
    stock_disponible = Column(Integer, nullable=False, default=0)
    fecha_registro = Column(DateTime, server_default=func.now())