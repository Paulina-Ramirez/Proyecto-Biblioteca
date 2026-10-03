from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.repositories.libro_repository import LibroRepository
from app.schemas.libro_schema import LibroCreate, LibroUpdate, LibroResponse

router = APIRouter(
    prefix="/libros",
    tags=["Libros"],
    responses={404: {"description": "Libro no encontrado"}}
)

@router.get("/", response_model=List[LibroResponse], summary="Listar todos los libros")
def listar_libros(db: Session = Depends(get_db)):
    """Devuelve todos los libros del catálogo."""
    return LibroRepository.listar_todos(db)

@router.get("/{id_libro}", response_model=LibroResponse, summary="Obtener un libro por ID")
def obtener_libro(id_libro: int, db: Session = Depends(get_db)):
    libro = LibroRepository.obtener_por_id(db, id_libro)
    if not libro:
        raise HTTPException(status_code=404, detail=f"Libro con ID {id_libro} no encontrado")
    return libro

@router.post("/", response_model=LibroResponse, status_code=status.HTTP_201_CREATED, summary="Crear un libro")
def crear_libro(libro: LibroCreate, db: Session = Depends(get_db)):
    # Validar que el ISBN no exista
    existente = LibroRepository.obtener_por_isbn(db, libro.isbn)
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un libro con ISBN {libro.isbn}")
    
    return LibroRepository.crear(
        db,
        isbn=libro.isbn,
        titulo=libro.titulo,
        autor=libro.autor,
        categoria=libro.categoria,
        stock_total=libro.stock_total
    )

@router.put("/{id_libro}", response_model=LibroResponse, summary="Actualizar un libro")
def actualizar_libro(id_libro: int, libro: LibroUpdate, db: Session = Depends(get_db)):
    existente = LibroRepository.obtener_por_id(db, id_libro)
    if not existente:
        raise HTTPException(status_code=404, detail=f"Libro con ID {id_libro} no encontrado")
    
    # Solo actualizar los campos que vienen con valor
    datos = libro.model_dump(exclude_unset=True)
    for key, value in datos.items():
        setattr(existente, key, value)
    
    db.commit()
    db.refresh(existente)
    return existente

@router.delete("/{id_libro}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un libro")
def eliminar_libro(id_libro: int, db: Session = Depends(get_db)):
    existente = LibroRepository.obtener_por_id(db, id_libro)
    if not existente:
        raise HTTPException(status_code=404, detail=f"Libro con ID {id_libro} no encontrado")
    LibroRepository.eliminar(db, id_libro)
    return None