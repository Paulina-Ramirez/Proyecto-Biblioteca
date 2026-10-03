from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Schema base (campos comunes)
class LibroBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=20, description="ISBN único del libro")
    titulo: str = Field(..., min_length=1, max_length=200)
    autor: str = Field(..., min_length=1, max_length=150)
    categoria: Optional[str] = Field(None, max_length=80)
    stock_total: int = Field(..., ge=0, description="Stock total (no puede ser negativo)")

# Schema para CREAR un libro (lo que envía el cliente)
class LibroCreate(LibroBase):
    pass  # Hereda todos los campos de LibroBase

# Schema para ACTUALIZAR (todos los campos opcionales)
class LibroUpdate(BaseModel):
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    autor: Optional[str] = Field(None, min_length=1, max_length=150)
    categoria: Optional[str] = Field(None, max_length=80)
    stock_total: Optional[int] = Field(None, ge=0)

# Schema para RESPONDER (lo que devuelve la API)
class LibroResponse(LibroBase):
    id_libro: int
    stock_disponible: int
    fecha_registro: datetime

    class Config:
        from_attributes = True  # Permite convertir modelos SQLAlchemy a Pydantic