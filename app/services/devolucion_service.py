"""
app/services/devolucion_service.py

Procesa la devolución de un préstamo dentro de UNA sola transacción.

Reglas:
    1. Se consulta la fecha_vencimiento del préstamo y se compara con la fecha de devolución.
    2. A tiempo (devolución <= vencimiento): se marca el préstamo como devuelto
       y el libro regresa al stock.
    3. Con retraso (devolución > vencimiento): además de lo anterior se calculan los
       días de retraso, la multa (dias_retraso * MONTO_SANCION_POR_DIA) y se crea
       una sanción para el usuario.

Equivalencia con los nombres pedidos en el enunciado:
    get_prestamo           -> PrestamoRepository.obtener_por_id
    update_prestamo_status -> PrestamoRepository.actualizar_estado_devolucion
    increase_book_stock    -> LibroRepository.aumentar_stock
    create_sancion         -> SancionRepository.crear
"""
import math
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.repositories.libro_repository import LibroRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.sancion_repository import SancionRepository

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
MONTO_SANCION_POR_DIA = Decimal("5.00")  # $5 por cada día de retraso

MSG_DEVOLUCION_EXITOSA = "Devolución exitosa"
MSG_DEVOLUCION_CON_RETRASO = (
    "Devolución registrada con retraso. Se generó una sanción de ${monto:.2f} "
    "por {dias} día(s) de retraso; debe pagarla para poder pedir un nuevo préstamo"
)


# ---------------------------------------------------------------------------
# Respuesta y errores
# ---------------------------------------------------------------------------
class DevolucionResponse(BaseModel):
    message: str
    data: Dict[str, Any]


class PrestamoYaDevuelto(Exception):
    """El préstamo ya fue devuelto antes (el router lo traduce a 400)."""


# ---------------------------------------------------------------------------
# Cálculo de la multa
# ---------------------------------------------------------------------------
def calcular_dias_retraso(fecha_vencimiento: datetime, fecha_devolucion: datetime) -> int:
    """
    Días de retraso redondeados HACIA ARRIBA: cualquier fracción de día cuenta
    como un día completo (1 hora tarde = 1 día). Devuelve 0 si llegó a tiempo.
    """
    if fecha_devolucion <= fecha_vencimiento:
        return 0
    segundos = (fecha_devolucion - fecha_vencimiento).total_seconds()
    return max(1, math.ceil(segundos / 86400))


# ---------------------------------------------------------------------------
# Devolución
# ---------------------------------------------------------------------------
def procesar_devolucion(
    db: Session,
    id_prestamo: int,
    fecha_devolucion: Optional[datetime] = None,
) -> DevolucionResponse:
    """
    Procesa la devolución de un préstamo.

    - Lanza LookupError si el préstamo no existe (404).
    - Lanza PrestamoYaDevuelto si ya estaba devuelto (400).
    - Todo o nada: marcar devuelto + aumentar stock + (si aplica) crear sanción
      se confirman juntos con UN commit. Si cualquier paso falla, se hace
      rollback de TODO y no queda nada a medias (por ejemplo, stock aumentado
      sin sanción).
    """
    # 1. Consulta del préstamo (solo lectura, aún no se modifica nada)
    prestamo = PrestamoRepository.obtener_por_id(db, id_prestamo)
    if prestamo is None:
        raise LookupError(f"Préstamo con ID {id_prestamo} no encontrado")
    if prestamo.estado == "Devuelto":
        raise PrestamoYaDevuelto("Este préstamo ya fue devuelto")

    # Se leen los datos ANTES de las escrituras (los UPDATE no refrescan el objeto)
    id_usuario = prestamo.id_usuario
    id_libro = prestamo.id_libro
    fecha_vencimiento = prestamo.fecha_vencimiento
    fecha_dev = fecha_devolucion or datetime.now()

    # 2. Evaluación: ¿entregado a tiempo?
    dias_retraso = calcular_dias_retraso(fecha_vencimiento, fecha_dev)
    monto = MONTO_SANCION_POR_DIA * dias_retraso  # Decimal; 0 si dias_retraso == 0

    # 3. Transacción: todas las escrituras con commit=False y un único commit al final
    try:
        # 3.1 Marcar como devuelto. El UPDATE solo aplica si NO estaba devuelto,
        #     así dos devoluciones simultáneas del mismo préstamo no suben el stock dos veces.
        filas = PrestamoRepository.actualizar_estado_devolucion(
            db, id_prestamo, fecha_dev, commit=False
        )
        if filas == 0:
            db.rollback()
            raise PrestamoYaDevuelto("Este préstamo ya fue devuelto")

        # 3.2 El libro vuelve al stock
        LibroRepository.aumentar_stock(db, id_libro, commit=False)

        # 3.3 Ruta con retraso: registrar la sanción
        if dias_retraso > 0:
            SancionRepository.crear(
                db,
                id_usuario=id_usuario,
                id_prestamo=id_prestamo,
                monto=monto,
                dias_retraso=dias_retraso,
                commit=False,
            )

        # 3.4 Todo salió bien: se confirma TODO junto
        db.commit()
    except PrestamoYaDevuelto:
        raise
    except Exception:
        # Falló cualquier paso (p. ej. create_sancion): se deshace todo,
        # incluido el aumento de stock y el cambio de estado del préstamo.
        db.rollback()
        raise

    # 4. Respuesta
    if dias_retraso == 0:
        return DevolucionResponse(
            message=MSG_DEVOLUCION_EXITOSA,
            data={
                "id_prestamo": id_prestamo,
                "fecha_devolucion": fecha_dev.isoformat(),
                "sancion": False,  # no hay sanción
            },
        )

    return DevolucionResponse(
        message=MSG_DEVOLUCION_CON_RETRASO.format(monto=monto, dias=dias_retraso),
        data={
            "id_prestamo": id_prestamo,
            "fecha_devolucion": fecha_dev.isoformat(),
            "sancion": True,
            "dias_retraso": dias_retraso,
            "monto_sancion": float(monto),
        },
    )
