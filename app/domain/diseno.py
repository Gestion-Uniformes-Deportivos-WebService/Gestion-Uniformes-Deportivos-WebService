from enum import Enum
from typing import Optional
from pydantic import BaseModel

from app.domain.errores import ReglaNegocioError, ValidacionDominioError


class EstadoDiseno(str, Enum):
    BORRADOR = "BORRADOR"
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    DISENO_APROBADO = "DISEÑO_APROBADO"
    RECHAZADO = "RECHAZADO"


class Diseno:
    """Entidad del dominio: arte de un pedido."""

    def __init__(self, id: int, id_pedido: int, archivo_arte: Optional[str],
                 estado: EstadoDiseno = EstadoDiseno.BORRADOR,
                 observaciones: Optional[str] = None):
        self.id = id
        self.id_pedido = id_pedido
        self.archivo_arte = archivo_arte
        self.estado = estado
        self.observaciones = observaciones

    def enviar_a_aprobacion(self) -> None:
        # RN-23: no hay nada que aprobar sin archivo de arte
        if not self.archivo_arte:
            raise ValidacionDominioError(
                "No se puede enviar a aprobación un diseño sin archivo de arte cargado",
                {"idDiseno": self.id},
            )
        if self.estado == EstadoDiseno.PENDIENTE_APROBACION:
            raise ReglaNegocioError(
                "El diseño ya está pendiente de aprobación", {"idDiseno": self.id}
            )
        if self.estado == EstadoDiseno.DISENO_APROBADO:
            raise ReglaNegocioError(
                "El diseño ya fue aprobado", {"idDiseno": self.id}
            )
        self.estado = EstadoDiseno.PENDIENTE_APROBACION


class DisenoAprobacionResponse(BaseModel):
    idDiseno: int
    idPedido: int
    estado: EstadoDiseno
    clienteNotificado: bool