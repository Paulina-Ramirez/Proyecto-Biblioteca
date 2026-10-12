"""
app/services/prestamo_service.py

Validación y registro de préstamos (enfoque fail-fast).
Orden de reglas:
    1. Disponibilidad del libro
    2. Sanciones pendientes del usuario
    3. Límite de 3 préstamos activos
    4. Éxito  -> registrar_prestamo() crea el préstamo y descuenta el stock
"""
from datetime import datetime, timedelta
from typing import Literal, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.prestamo import Prestamo
from app.repositories.libro_repository import LibroRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.sancion_repository import SancionRepository
from app.schemas.prestamo_schema import PrestamoCreate

# ---------------------------------------------------------------------------
# Constantes (mensajes exactos solicitados)
# ---------------------------------------------------------------------------
LIMITE_PRESTAMOS = {
    "Estudiante": 3,
    "Docente": 5,
    "Bibliotecario": 10,
}
LIMITE_PRESTAMOS_POR_DEFECTO = 3  # por si llega un rol no contemplado

MSG_LIBRO_NO_DISPONIBLE = "Libro no disponible"
MSG_SANCION_PENDIENTE = "Sancion pendiente porfavor pagar para poder pedir un prestamo"
# El número se completa según el rol; para Estudiante queda exactamente:
# "Ya tienes el limite de 3 prestamos activos"
MSG_LIMITE_PRESTAMOS = "Ya tienes el limite de {limite} prestamos activos"

MSG_LIBRO_NO_DISPONIBLE = "Libro no disponible"
MSG_SANCION_PENDIENTE = "Sancion pendiente porfavor pagar para poder pedir un prestamo"
MSG_LIMITE_PRESTAMOS = "Ya tienes el limite de 3 prestamos activos"
MSG_EXITO = "Solicitud válida, puede proceder con el préstamo"


# ---------------------------------------------------------------------------
# Resultado de la validación
# (puedes moverlo a schemas/prestamo_schema.py si prefieres)
# ---------------------------------------------------------------------------
class ValidacionPrestamoResponse(BaseModel):
    valido: bool
    mensaje: str
    motivo: Optional[Literal["NO_DISPONIBLE", "SANCION", "LIMITE_PRESTAMOS"]] = None
    fecha_devolucion_cercana: Optional[datetime] = None


class PrestamoNoPermitido(Exception):
    """Se lanza cuando la solicitud no supera alguna de las validaciones."""

    def __init__(self, resultado: ValidacionPrestamoResponse):
        self.resultado = resultado
        super().__init__(resultado.mensaje)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _rechazo_no_disponible(db: Session, libro_id: int) -> ValidacionPrestamoResponse:
    """Arma el rechazo por falta de stock con la fecha de devolución más cercana
    (solo préstamos activos, sin devolver y con vencimiento >= ahora)."""
    fecha_cercana = PrestamoRepository.obtener_fecha_vencimiento_mas_cercana(
        db, libro_id, desde=datetime.now()
    )
    return ValidacionPrestamoResponse(
        valido=False,
        mensaje=MSG_LIBRO_NO_DISPONIBLE,
        motivo="NO_DISPONIBLE",
        fecha_devolucion_cercana=fecha_cercana,
    )


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------
def validar_solicitud_prestamo(
    db: Session, usuario_id: int, libro_id: int
) -> ValidacionPrestamoResponse:
    """
    Valida si un usuario puede pedir prestado un libro.
    Lanza LookupError si el usuario o el libro no existen (el router lo traduce a 404).
    """
    # --- Existencia de entidades (integridad, no regla de negocio) ---
    usuario = UsuarioRepository.obtener_por_id(db, usuario_id)
    if usuario is None:
        raise LookupError(f"Usuario con ID {usuario_id} no encontrado")

    libro = LibroRepository.obtener_por_id(db, libro_id)
    if libro is None:
        raise LookupError(f"Libro con ID {libro_id} no encontrado")

    # --- 1. Disponibilidad ---
    if libro.stock_disponible <= 0:
        return _rechazo_no_disponible(db, libro_id)

    # --- 2. Sanciones activas (no pagadas) ---
    if SancionRepository.usuario_tiene_sancion_pendiente(db, usuario_id):
        return ValidacionPrestamoResponse(
            valido=False, mensaje=MSG_SANCION_PENDIENTE, motivo="SANCION"
        )

     # --- 3. Límite de préstamos activos (según el rol) ---
    limite = LIMITE_PRESTAMOS.get(usuario.rol, LIMITE_PRESTAMOS_POR_DEFECTO)
    if PrestamoRepository.contar_activos_por_usuario(db, usuario_id) >= limite:
        return ValidacionPrestamoResponse(
            valido=False,
            mensaje=MSG_LIMITE_PRESTAMOS.format(limite=limite),
            motivo="LIMITE_PRESTAMOS",
        )

    # --- 4. Éxito ---
    return ValidacionPrestamoResponse(valido=True, mensaje=MSG_EXITO)


# ---------------------------------------------------------------------------
# Registro del préstamo (valida + crea préstamo + descuenta stock)
# ---------------------------------------------------------------------------
def registrar_prestamo(db: Session, datos: PrestamoCreate) -> Prestamo:
    """
    Registra el préstamo si supera las validaciones.

    - Lanza LookupError si el usuario o el libro no existen.
    - Lanza PrestamoNoPermitido si alguna regla falla.
    - La creación del préstamo y el descuento de stock se hacen en UNA sola
      transacción: si algo falla, no se guarda ninguno de los dos.
    """
    validacion = validar_solicitud_prestamo(db, datos.id_usuario, datos.id_libro)
    if not validacion.valido:
        raise PrestamoNoPermitido(validacion)

    fecha_vencimiento = datetime.now() + timedelta(days=datos.dias_prestamo)

    try:
        # UPDATE atómico: solo descuenta si todavía hay stock. Si dos solicitudes
        # llegan a la vez por la última copia, solo una obtiene filas == 1.
        filas = LibroRepository.descontar_stock(db, datos.id_libro, commit=False)
        if filas == 0:
            db.rollback()
            raise PrestamoNoPermitido(_rechazo_no_disponible(db, datos.id_libro))

        nuevo = PrestamoRepository.crear(
            db,
            id_usuario=datos.id_usuario,
            id_libro=datos.id_libro,
            fecha_vencimiento=fecha_vencimiento,
            commit=False,
        )
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except PrestamoNoPermitido:
        raise
    except Exception:
        db.rollback()
        raise
