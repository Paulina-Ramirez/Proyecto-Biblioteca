from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

# Schema para CREAR un préstamo
class PrestamoCreate(BaseModel):
    id_usuario: int = Field(..., gt=0)
    id_libro: int = Field(..., gt=0)
    dias_prestamo: int = Field(7, ge=1, le=30, description="Días de préstamo (por defecto 7)")

# Schema para RESPONDER
class PrestamoResponse(BaseModel):
    id_prestamo: int
    id_usuario: int
    id_libro: int
    fecha_prestamo: datetime
    fecha_vencimiento: datetime
    fecha_devolucion: Optional[datetime] = None
    estado: Literal["Activo", "Devuelto", "Vencido"]

    class Config:
        from_attributes = True

# Schema para DEVOLVER un préstamo
class PrestamoDevolucion(BaseModel):
    fecha_devolucion: Optional[datetime] = Field(None, description="Fecha de devolución (si no se envía, se usa la fecha actual)")