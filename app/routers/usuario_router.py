from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    responses={404: {"description": "Usuario no encontrado"}}
)

@router.get("/", response_model=List[UsuarioResponse], summary="Listar todos los usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return UsuarioRepository.listar_todos(db)

@router.get("/{id_usuario}", response_model=UsuarioResponse, summary="Obtener usuario por ID")
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = UsuarioRepository.obtener_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")
    return usuario

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, summary="Crear un usuario")
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Validar email único
    existente = UsuarioRepository.obtener_por_email(db, usuario.email)
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un usuario con email {usuario.email}")
    
    # ⚠️ TODO: Aquí iría el hash de la contraseña (lo veremos después)
    # Por ahora guardamos el password tal cual (SOLO PARA PRUEBAS)
    password_hash = f"hash_{usuario.password}"  # ← TEMPORAL, cambiar después
    
    return UsuarioRepository.crear(
        db,
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=password_hash,
        rol=usuario.rol
    )

@router.put("/{id_usuario}", response_model=UsuarioResponse, summary="Actualizar un usuario")
def actualizar_usuario(id_usuario: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    existente = UsuarioRepository.obtener_por_id(db, id_usuario)
    if not existente:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")
    
    datos = usuario.model_dump(exclude_unset=True)
    for key, value in datos.items():
        setattr(existente, key, value)
    
    db.commit()
    db.refresh(existente)
    return existente

@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un usuario")
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    existente = UsuarioRepository.obtener_por_id(db, id_usuario)
    if not existente:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")
    UsuarioRepository.eliminar(db, id_usuario)
    return None

# --- RUTA TEMPORAL DE LOGIN PARA QUE EL FRONTEND PUEDA PROBAR ---
@router.post("/login", summary="Iniciar sesión")
def login_usuario(datos: dict, db: Session = Depends(get_db)):
    email = datos.get("email")
    password = datos.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email y contraseña son requeridos")
        
    usuario = UsuarioRepository.obtener_por_email(db, email)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    # En el archivo original, el hash se guarda como "hash_{password}". 
    # Lo comparamos así para que funcione ahora:
    if usuario.password_hash != f"hash_{password}":
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    return {
        "mensaje": "Login exitoso", 
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "rol": usuario.rol
    }