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
COSTO_UNITARIO_DEFAULT = 45_000  # tarifa base por unidad, si no hay parámetro
# RN-03: en estos estados el pedido ya no puede modificarse
ESTADOS_NO_MODIFICABLES = ("EN_PRODUCCION", "LISTO_PARA_DESPACHO", "ENTREGADO")
ESTADO_EN_PRODUCCION = "EN_PRODUCCION"


# ── Validación del id de pedido recibido por la ruta ─────────
# (función de módulo: va FUERA de cualquier clase, sin sangría)
def validar_id_pedido(valor: str) -> int:
    """El id llega como texto en la URL; debe ser un número entero positivo."""
    valor = (valor or "").strip()
    if not valor.isdigit() or int(valor) <= 0:
        raise ValueError("Identificador de pedido no válido. Debe ser numérico")
    return int(valor)


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


# ── Schemas de SALIDA ─────────────────────────────────────────
class PedidoResponse(BaseModel):
    idPedido: int
    idCliente: int
    cantidad: int
    estado: str
    esquemaPago: str


class CotizacionResponse(BaseModel):
    idPedido: int
    cantidad: int
    costoUnitario: int
    costoTotal: int
    anticipo: int
    saldoFinal: int


# ── Objeto de valor: esquema de pago (RN-14) ──────────────────
@dataclass(frozen=True)
class EsquemaDePago:
    anticipo: int = 50
    saldo: int = 50

    def validar(self) -> None:
        if self.anticipo != 50 or self.saldo != 50:
            raise ValueError("El pago debe dividirse en 50% de anticipo y 50% de saldo")

    # RN-50: el anticipo y el saldo se recalculan cuando cambia el valor total
    def recalcular(self, costo_total: int) -> tuple[int, int]:
        self.validar()  # RN-14: siempre 50/50
        anticipo = costo_total * self.anticipo // 100
        saldo = costo_total - anticipo  # el saldo absorbe cualquier redondeo
        return anticipo, saldo

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

    def calcular_costo_total(self, costo_unitario: int) -> int:
        return self.cantidad * costo_unitario

    # RN-03: un pedido no puede modificarse una vez esté en producción
    def validar_modificable(self) -> None:
        if self.estado in ESTADOS_NO_MODIFICABLES:
            raise ValueError(
                f"El pedido no puede modificarse porque está en estado {self.estado}"
            )

    # RN-07: no se autoriza producción si el diseño no está DISEÑO_APROBADO
    def autorizar_produccion(self, diseno_aprobado: bool) -> str:
        """Valida RN-07 y devuelve el estado destino (el servicio lo persiste)."""
        if not diseno_aprobado:
            raise ValueError("No se puede autorizar producción: el diseño no está aprobado")
        return ESTADO_EN_PRODUCCION

    # RN-16: no se genera guía de despacho sin saldo final pagado
    def tiene_paz_y_salvo(self, saldo_pendiente: int) -> bool:
        return saldo_pendiente == 0

    def to_response(self) -> dict:
        return {
            "idPedido": self.id,
            "idCliente": self.id_cliente,
            "cantidad": self.cantidad,
            "estado": self.estado,
            "esquemaPago": str(self.esquema_pago),
        }