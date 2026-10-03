from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

# Schema para RESPONDER
class SancionResponse(BaseModel):
    id_sancion: int
    id_usuario: int
    id_prestamo: int
    monto: Decimal
    dias_retraso: int
    pagada: bool
    fecha_sancion: datetime

    class Config:
        from_attributes = True