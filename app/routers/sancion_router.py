from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.repositories.sancion_repository import SancionRepository
from app.schemas.sancion_schema import SancionResponse

router = APIRouter(
    prefix="/sanciones",
    tags=["Sanciones"],
    responses={404: {"description": "Sanción no encontrada"}}
)


@router.get("/", response_model=List[SancionResponse], summary="Listar todas las sanciones")
def listar_sanciones(db: Session = Depends(get_db)):
    return SancionRepository.listar_todas(db)


@router.get("/usuario/{id_usuario}", response_model=List[SancionResponse], summary="Listar sanciones de un usuario")
def listar_sanciones_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return SancionRepository.listar_por_usuario(db, id_usuario)


@router.get("/usuario/{id_usuario}/pendientes", response_model=List[SancionResponse], summary="Listar sanciones pendientes de un usuario")
def listar_sanciones_pendientes(id_usuario: int, db: Session = Depends(get_db)):
    return SancionRepository.listar_pendientes_por_usuario(db, id_usuario)


@router.get("/{id_sancion}", response_model=SancionResponse, summary="Obtener una sanción por ID")
def obtener_sancion(id_sancion: int, db: Session = Depends(get_db)):
    sancion = SancionRepository.obtener_por_id(db, id_sancion)
    if not sancion:
        raise HTTPException(status_code=404, detail=f"Sanción con ID {id_sancion} no encontrada")
    return sancion


@router.put("/{id_sancion}/pagar", response_model=SancionResponse, summary="Marcar una sanción como pagada")
def pagar_sancion(id_sancion: int, db: Session = Depends(get_db)):
    sancion = SancionRepository.obtener_por_id(db, id_sancion)
    if not sancion:
        raise HTTPException(status_code=404, detail=f"Sanción con ID {id_sancion} no encontrada")
    if sancion.pagada:
        raise HTTPException(status_code=400, detail="Esta sanción ya fue pagada")
    return SancionRepository.marcar_como_pagada(db, id_sancion)