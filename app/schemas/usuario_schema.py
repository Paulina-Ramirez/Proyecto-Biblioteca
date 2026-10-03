from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from typing import Literal

# Schema base
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email único del usuario")
    rol: Literal["Estudiante", "Docente", "Bibliotecario"] = Field(..., description="Rol del usuario")

# Schema para CREAR
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña en texto plano (se hasheará)")

# Schema para ACTUALIZAR
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    rol: Optional[Literal["Estudiante", "Docente", "Bibliotecario"]] = None
    activo: Optional[bool] = None

# Schema para RESPONDER (NO incluye password_hash por seguridad)
class UsuarioResponse(UsuarioBase):
    id_usuario: int
    activo: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True