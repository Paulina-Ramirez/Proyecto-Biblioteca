from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.config.database import get_db
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.sancion_repository import SancionRepository
from app.schemas.prestamo_schema import PrestamoCreate, PrestamoResponse, PrestamoDevolucion
from app.services.prestamo_service import (
    ValidacionPrestamoResponse,
    PrestamoNoPermitido,
    validar_solicitud_prestamo,
    registrar_prestamo,
)
from app.services.devolucion_service import (
    DevolucionResponse, PrestamoYaDevuelto, procesar_devolucion,
)

router = APIRouter(
    prefix="/prestamos",
    tags=["Préstamos"],
    responses={404: {"description": "Préstamo no encontrado"}}
)

# ==========================================
# Reglas de negocio (RF4)
# El límite de préstamos activos (3) y las validaciones de préstamo
# viven ahora en app/services/prestamo_service.py
# ==========================================
MONTO_SANCION_POR_DIA = 5.00  # $5 por cada día de retraso

# Código HTTP según el motivo del rechazo
CODIGO_HTTP_RECHAZO = {
    "NO_DISPONIBLE": status.HTTP_400_BAD_REQUEST,
    "SANCION": status.HTTP_403_FORBIDDEN,
    "LIMITE_PRESTAMOS": status.HTTP_400_BAD_REQUEST,
}


@router.get("/", response_model=List[PrestamoResponse], summary="Listar todos los préstamos")
def listar_prestamos(db: Session = Depends(get_db)):
    return PrestamoRepository.listar_todos(db)


@router.get("/activos", response_model=List[PrestamoResponse], summary="Listar préstamos activos")
def listar_prestamos_activos(db: Session = Depends(get_db)):
    return PrestamoRepository.listar_activos(db)


@router.get("/usuario/{id_usuario}", response_model=List[PrestamoResponse], summary="Listar préstamos de un usuario")
def listar_prestamos_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return PrestamoRepository.listar_por_usuario(db, id_usuario)


# OJO: esta ruta debe ir ANTES de "/{id_prestamo}" para que "validar" no se
# interprete como un id.
@router.get("/validar", response_model=ValidacionPrestamoResponse, summary="Validar solicitud de préstamo (sin registrarlo)")
def validar_prestamo(usuario_id: int, libro_id: int, db: Session = Depends(get_db)):
    try:
        resultado = validar_solicitud_prestamo(db, usuario_id, libro_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not resultado.valido:
        raise HTTPException(
            status_code=CODIGO_HTTP_RECHAZO[resultado.motivo],
            detail=resultado.model_dump(mode="json")
        )
    return resultado


@router.get("/{id_prestamo}", response_model=PrestamoResponse, summary="Obtener un préstamo por ID")
def obtener_prestamo(id_prestamo: int, db: Session = Depends(get_db)):
    prestamo = PrestamoRepository.obtener_por_id(db, id_prestamo)
    if not prestamo:
        raise HTTPException(status_code=404, detail=f"Préstamo con ID {id_prestamo} no encontrado")
    return prestamo


@router.post("/", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED, summary="Registrar un préstamo (RF3)")
def crear_prestamo(prestamo: PrestamoCreate, db: Session = Depends(get_db)):
    """
    Valida (disponibilidad -> sanciones -> límite de 3 activos), crea el préstamo
    y descuenta el stock disponible en una sola transacción.
    """
    try:
        return registrar_prestamo(db, prestamo)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PrestamoNoPermitido as e:
        raise HTTPException(
            status_code=CODIGO_HTTP_RECHAZO[e.resultado.motivo],
            detail=e.resultado.model_dump(mode="json")
        )


@router.post("/devolucion", response_model=DevolucionResponse, summary="Registrar devolución (RF4)")
def registrar_devolucion(devolucion: PrestamoDevolucion, id_prestamo: int, db: Session = Depends(get_db)):
    try:
        return procesar_devolucion(db, id_prestamo, devolucion.fecha_devolucion)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PrestamoYaDevuelto as e:
        raise HTTPException(status_code=400, detail=str(e))
