from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.config.database import get_db
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.sancion_repository import SancionRepository
from app.schemas.prestamo_schema import PrestamoCreate, PrestamoResponse, PrestamoDevolucion

router = APIRouter(
    prefix="/prestamos",
    tags=["Préstamos"],
    responses={404: {"description": "Préstamo no encontrado"}}
)

# ==========================================
# Reglas de negocio (RF3 y RF4)
# ==========================================
LIMITE_PRESTAMOS = {
    "Estudiante": 3,
    "Docente": 5,
    "Bibliotecario": 10
}
MONTO_SANCION_POR_DIA = 5.00  # $5 por cada día de retraso


@router.get("/", response_model=List[PrestamoResponse], summary="Listar todos los préstamos")
def listar_prestamos(db: Session = Depends(get_db)):
    return PrestamoRepository.listar_todos(db)


@router.get("/activos", response_model=List[PrestamoResponse], summary="Listar préstamos activos")
def listar_prestamos_activos(db: Session = Depends(get_db)):
    return PrestamoRepository.listar_activos(db)


@router.get("/usuario/{id_usuario}", response_model=List[PrestamoResponse], summary="Listar préstamos de un usuario")
def listar_prestamos_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return PrestamoRepository.listar_por_usuario(db, id_usuario)


@router.get("/{id_prestamo}", response_model=PrestamoResponse, summary="Obtener un préstamo por ID")
def obtener_prestamo(id_prestamo: int, db: Session = Depends(get_db)):
    prestamo = PrestamoRepository.obtener_por_id(db, id_prestamo)
    if not prestamo:
        raise HTTPException(status_code=404, detail=f"Préstamo con ID {id_prestamo} no encontrado")
    return prestamo


@router.post("/", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED, summary="Registrar un préstamo (RF3)")
def crear_prestamo(prestamo: PrestamoCreate, db: Session = Depends(get_db)):
    # 1. Validar que el usuario exista
    usuario = UsuarioRepository.obtener_por_id(db, prestamo.id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {prestamo.id_usuario} no encontrado")
    
    # 2. Validar que el libro exista
    libro = LibroRepository.obtener_por_id(db, prestamo.id_libro)
    if not libro:
        raise HTTPException(status_code=404, detail=f"Libro con ID {prestamo.id_libro} no encontrado")
    
    # 3. Validar disponibilidad física (RF3)
    if libro.stock_disponible <= 0:
        raise HTTPException(status_code=400, detail=f"No hay ejemplares disponibles del libro '{libro.titulo}'")
    
    # 4. Validar que el usuario no tenga sanciones pendientes (RF4)
    if SancionRepository.usuario_tiene_sancion_pendiente(db, prestamo.id_usuario):
        raise HTTPException(status_code=403, detail=f"El usuario {usuario.nombre} tiene sanciones pendientes. Debe pagarlas antes de pedir más préstamos.")
    
    # 5. Validar límite de préstamos activos (RF3)
    prestamos_activos = PrestamoRepository.contar_activos_por_usuario(db, prestamo.id_usuario)
    limite = LIMITE_PRESTAMOS.get(usuario.rol, 3)
    if prestamos_activos >= limite:
        raise HTTPException(
            status_code=400,
            detail=f"El usuario {usuario.nombre} ({usuario.rol}) ya tiene {prestamos_activos} préstamos activos. Límite: {limite}."
        )
    
    # 6. Calcular fecha de vencimiento
    fecha_vencimiento = datetime.now() + timedelta(days=prestamo.dias_prestamo)
    
    # 7. Crear el préstamo
    nuevo_prestamo = PrestamoRepository.crear(
        db,
        id_usuario=prestamo.id_usuario,
        id_libro=prestamo.id_libro,
        fecha_vencimiento=fecha_vencimiento
    )
    
    # 8. Reducir el stock disponible
    LibroRepository.actualizar_stock(db, libro.id_libro, libro.stock_disponible - 1)
    
    return nuevo_prestamo


@router.post("/devolucion", response_model=PrestamoResponse, summary="Registrar devolución (RF4)")
def registrar_devolucion(devolucion: PrestamoDevolucion, id_prestamo: int, db: Session = Depends(get_db)):
    # 1. Validar que el préstamo exista
    prestamo = PrestamoRepository.obtener_por_id(db, id_prestamo)
    if not prestamo:
        raise HTTPException(status_code=404, detail=f"Préstamo con ID {id_prestamo} no encontrado")
    
    if prestamo.estado == "Devuelto":
        raise HTTPException(status_code=400, detail="Este préstamo ya fue devuelto")
    
    # 2. Calcular fecha de devolución
    fecha_dev = devolucion.fecha_devolucion or datetime.now()
    
    # 3. Registrar la devolución
    prestamo_actualizado = PrestamoRepository.registrar_devolucion(db, id_prestamo, fecha_dev)
    
    # 4. Aumentar el stock disponible del libro
    libro = LibroRepository.obtener_por_id(db, prestamo.id_libro)
    if libro:
        LibroRepository.actualizar_stock(db, libro.id_libro, libro.stock_disponible + 1)
    
    # 5. Calcular sanción si hay retraso (RF4)
    if fecha_dev > prestamo.fecha_vencimiento:
        dias_retraso = (fecha_dev - prestamo.fecha_vencimiento).days
        monto = dias_retraso * MONTO_SANCION_POR_DIA
        SancionRepository.crear(
            db,
            id_usuario=prestamo.id_usuario,
            id_prestamo=prestamo.id_prestamo,
            monto=monto,
            dias_retraso=dias_retraso
        )
    
    return prestamo_actualizado