from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from app.domain.errores import ReglaNegocioError


class TipoMovimiento(str, Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"


class Insumo:
    """Entidad del dominio: materia prima con su stock."""

    def __init__(self, nombre: str, stock: int):
        self.nombre = nombre
        self.stock = stock

    def registrar_entrada(self, cantidad: int) -> None:
        self.stock += cantidad

    def registrar_salida(self, cantidad: int) -> None:
        # RN-32 y RN-37: no se saca más de lo disponible ni queda stock negativo
        if cantidad > self.stock:
            raise ReglaNegocioError(
                "La salida supera la cantidad disponible del insumo",
                {"cantidadSolicitada": cantidad, "cantidadDisponible": self.stock},
            )
        self.stock -= cantidad


class MovimientoInventario:
    def __init__(self, id: int, insumo: str, tipo: TipoMovimiento,
                 cantidad: int, saldo_disponible: int):
        self.id = id
        self.insumo = insumo
        self.tipo = tipo
        self.cantidad = cantidad
        self.saldo_disponible = saldo_disponible


class MovimientoRequest(BaseModel):
    insumo: str = Field(..., min_length=1)
    tipo: TipoMovimiento
    cantidad: int = Field(..., gt=0)


class MovimientoResponse(BaseModel):
    idMovimiento: int
    insumo: str
    tipo: TipoMovimiento
    cantidad: int
    saldoDisponible: int