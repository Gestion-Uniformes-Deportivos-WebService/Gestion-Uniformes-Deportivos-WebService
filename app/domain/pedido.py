# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — Pedido (MOD-01 / SUB-01)
# RN-01: todo pedido debe tener mínimo 6 unidades (configurable).
# RN-02: no se crea un pedido sin un cliente activo.
# RN-12: el cliente debe tener al menos una dirección de envío.
# RN-14: el pago se divide obligatoriamente en 50% anticipo y 50% saldo.
# ─────────────────────────────────────────────────────────────

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.domain.cliente import Cliente

CANTIDAD_MINIMA_DEFAULT = 6
ESTADO_PENDIENTE_ANTICIPO = "PENDIENTE_ANTICIPO"


# ── Schemas de ENTRADA ────────────────────────────────────────
class PrendaCreate(BaseModel):
    prenda: str = Field(..., description="Tipo de prenda (ej. Camiseta)")
    talla: str = Field(..., description="Talla (ej. M)")
    color: str = Field(..., description="Color (ej. Azul)")

    @field_validator("prenda", "talla", "color")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Los campos de la prenda no pueden estar vacíos")
        return v


class PedidoCreate(BaseModel):
    idCliente: int = Field(..., gt=0, description="ID del cliente activo")
    listaPrendas: list[PrendaCreate] = Field(..., min_length=1,
                                             description="Prendas del pedido")
    # Solo exige > 0; la cantidad mínima (RN-01) es una regla de negocio → 422
    cantidad: int = Field(..., gt=0, description="Total de unidades del pedido")


# ── Schema de SALIDA ──────────────────────────────────────────
class PedidoResponse(BaseModel):
    idPedido: int
    idCliente: int
    cantidad: int
    estado: str
    esquemaPago: str


# ── Objeto de valor: esquema de pago (RN-14) ──────────────────
@dataclass(frozen=True)
class EsquemaDePago:
    anticipo: int = 50
    saldo: int = 50

    def validar(self) -> None:
        if self.anticipo != 50 or self.saldo != 50:
            raise ValueError("El pago debe dividirse en 50% de anticipo y 50% de saldo")

    def __str__(self) -> str:
        return f"{self.anticipo}/{self.saldo}"


# ── Entidad: pedido ───────────────────────────────────────────
class Pedido:
    def __init__(self, id: int, id_cliente: int, prendas: list[dict],
                 cantidad: int, estado: str, esquema_pago: EsquemaDePago):
        self.id = id
        self.id_cliente = id_cliente
        self.prendas = prendas
        self.cantidad = cantidad
        self.estado = estado
        self.esquema_pago = esquema_pago

    # RN-02: el pedido exige un cliente existente y activo
    @staticmethod
    def validar_cliente_activo(cliente: Optional[Cliente]) -> None:
        if cliente is None or not cliente.esta_activo():
            raise ValueError("El cliente no existe o no está activo")

    # RN-01: cantidad mínima de unidades
    def validar_cantidad_minima(self, minimo: int) -> None:
        if self.cantidad < minimo:
            raise ValueError(
                f"El pedido no cumple la cantidad mínima de {minimo} unidades"
            )

    def to_response(self) -> dict:
        return {
            "idPedido": self.id,
            "idCliente": self.id_cliente,
            "cantidad": self.cantidad,
            "estado": self.estado,
            "esquemaPago": str(self.esquema_pago),
        }