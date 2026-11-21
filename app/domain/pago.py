# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — Pago (MOD-03 / SUB-05)
# RN-14: el pago se divide 50% anticipo y 50% saldo (EsquemaDePago).
# RN-17: un abono no puede superar el valor pendiente del pedido.
# RN-19: no se registran pagos con monto cero o negativo.
# RN-20: un pedido CANCELADO no puede recibir nuevos pagos.
# No importa nada de FastAPI ni de almacenamiento.
# ─────────────────────────────────────────────────────────────

from dataclasses import dataclass

from pydantic import BaseModel, Field, field_validator

from app.domain.pedido import EsquemaDePago

TIPO_ANTICIPO = "ANTICIPO"
ESTADO_PAGO_ABONADO = "ABONADO"   # el acumulado ya alcanzó el 50%
ESTADO_PAGO_PARCIAL = "PARCIAL"   # aún no alcanza el 50%
ESTADO_PEDIDO_CANCELADO = "CANCELADO"


# ── Utilidades de formato para los mensajes ───────────────────
def formatear_pesos(valor: int) -> str:
    """540000 → $540.000"""
    return "$" + f"{valor:,}".replace(",", ".")


def formatear_porcentaje(valor: float) -> str:
    """70.0 → 70% ; 18.518 → 18.5%"""
    return f"{round(valor, 1):g}%"


# ── Schema de ENTRADA (body del POST) ─────────────────────────
class PagoAnticipoCreate(BaseModel):
    idPedido: int = Field(..., gt=0, description="ID del pedido")
    monto: int = Field(..., description="Valor pagado, en pesos enteros")
    comprobante: str = Field(..., description="Comprobante o token de la transacción")

    @field_validator("monto")
    @classmethod
    def monto_positivo(cls, v: int) -> int:
        if v <= 0:  # RN-19
            raise ValueError("El monto debe ser mayor a cero")
        return v

    @field_validator("comprobante")
    @classmethod
    def comprobante_valido(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("El comprobante debe tener al menos 5 caracteres")
        return v


# ── Schema de SALIDA (data del JSON) ──────────────────────────
class PagoResponse(BaseModel):
    idPago: int
    idPedido: int
    monto: int
    tipo: str
    estadoPago: str


# ── Objeto de valor: resumen de lo pagado de un pedido ────────
@dataclass(frozen=True)
class ResumenPago:
    total: int    # valor total del pedido
    pagado: int   # suma de los abonos registrados

    @property
    def pendiente(self) -> int:
        return max(self.total - self.pagado, 0)

    @property
    def porcentaje_pagado(self) -> float:
        return 0.0 if self.total == 0 else self.pagado * 100 / self.total

    @property
    def porcentaje_pendiente(self) -> float:
        return 100.0 - self.porcentaje_pagado

    @property
    def anticipo_requerido(self) -> int:
        # RN-14: el anticipo es el 50% del total
        return EsquemaDePago().recalcular(self.total)[0]

    @property
    def faltante_anticipo(self) -> int:
        return max(self.anticipo_requerido - self.pagado, 0)

    def anticipo_completo(self) -> bool:
        return self.pagado >= self.anticipo_requerido

    def etapa_pago(self) -> str:
        """Etapa del pago que se muestra en la consulta de estado (HU-005)."""
        if self.pagado <= 0:
            return "ANTICIPO_PENDIENTE"
        if self.pagado >= self.total:
            return "PAGO_COMPLETO"
        if self.anticipo_completo():
            return "ANTICIPO_VERIFICADO"
        return "ANTICIPO_PARCIAL"

    def mensaje_abono(self) -> str:
        texto = (
            f"Ha abonado {formatear_pesos(self.pagado)} "
            f"({formatear_porcentaje(self.porcentaje_pagado)}) y debe "
            f"{formatear_pesos(self.pendiente)} "
            f"({formatear_porcentaje(self.porcentaje_pendiente)})."
        )
        if not self.anticipo_completo():
            texto += (
                f" Faltan {formatear_pesos(self.faltante_anticipo)} "
                f"para completar el anticipo del 50%."
            )
        return texto


# ── Entidad: pago ─────────────────────────────────────────────
class Pago:
    def __init__(self, id: int, id_pedido: int, monto: int,
                 tipo: str, comprobante: str, estado: str):
        self.id = id
        self.id_pedido = id_pedido
        self.monto = monto
        self.tipo = tipo
        self.comprobante = comprobante
        self.estado = estado

    # RN-20: el pedido debe estar activo (no CANCELADO)
    @staticmethod
    def pedido_activo(estado_pedido: str) -> None:
        if estado_pedido == ESTADO_PEDIDO_CANCELADO:
            raise ValueError("Un pedido CANCELADO no puede recibir nuevos pagos")

    # RN-17: el abono no puede superar el valor pendiente
    def validar_monto(self, valor_pendiente: int) -> None:
        if self.monto > valor_pendiente:
            raise ValueError("El monto supera el valor pendiente del pedido")

    def to_response(self) -> dict:
        return {
            "idPago": self.id,
            "idPedido": self.id_pedido,
            "monto": self.monto,
            "tipo": self.tipo,
            "estadoPago": self.estado,
        }