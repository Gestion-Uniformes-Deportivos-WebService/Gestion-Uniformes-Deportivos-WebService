# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — EstadoPedido (MOD-01 / SUB-03)
# RN-06: el estado avanza únicamente en la secuencia
#        PENDIENTE_ANTICIPO → EN_PRODUCCION → LISTO_PARA_DESPACHO → ENTREGADO
# No importa nada de FastAPI ni de almacenamiento.
# ─────────────────────────────────────────────────────────────

from typing import Optional

from pydantic import BaseModel


# ── Schema de SALIDA (data del JSON) ──────────────────────────
class EstadoPedidoResponse(BaseModel):
    idPedido: int
    estado: str
    pago: str
    produccion: str
    despacho: str


class EstadoPedido:
    # RN-06: secuencia única permitida
    SECUENCIA = (
        "PENDIENTE_ANTICIPO",
        "EN_PRODUCCION",
        "LISTO_PARA_DESPACHO",
        "ENTREGADO",
    )

    # Etapas de pago, producción y despacho que corresponden a cada estado
    DETALLE_POR_ESTADO = {
        "PENDIENTE_ANTICIPO": {
            "pago": "ANTICIPO_PENDIENTE", "produccion": "NO_INICIADA", "despacho": "PENDIENTE",
        },
        "EN_PRODUCCION": {
            "pago": "ANTICIPO_VERIFICADO", "produccion": "EN_CONFECCION", "despacho": "PENDIENTE",
        },
        "LISTO_PARA_DESPACHO": {
            "pago": "ANTICIPO_VERIFICADO", "produccion": "FINALIZADA", "despacho": "LISTO",
        },
        "ENTREGADO": {
            "pago": "PAGO_COMPLETO", "produccion": "FINALIZADA", "despacho": "ENTREGADO",
        },
    }

    @classmethod
    def es_valido(cls, estado: str) -> bool:
        return estado in cls.SECUENCIA

    @classmethod
    def siguiente(cls, estado: str) -> Optional[str]:
        """Estado que sigue en la secuencia (None si ya es el último)."""
        i = cls.SECUENCIA.index(estado)
        return cls.SECUENCIA[i + 1] if i + 1 < len(cls.SECUENCIA) else None

    # RN-06: solo se permite avanzar al estado inmediatamente siguiente
    @classmethod
    def puede_avanzar(cls, actual: str, nuevo: str) -> bool:
        return cls.es_valido(actual) and cls.siguiente(actual) == nuevo

    @classmethod
    def detalle(cls, estado: str) -> dict:
        """Devuelve pago, producción y despacho del estado; ValueError si no existe."""
        if not cls.es_valido(estado):
            raise ValueError(f"El estado '{estado}' no pertenece a la secuencia del pedido")
        return dict(cls.DETALLE_POR_ESTADO[estado])