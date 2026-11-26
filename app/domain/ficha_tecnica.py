# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — FichaTecnica (MOD-01 / SUB-02)
# RN-08: la cantidad de tallas/dorsales/nombres debe coincidir con las
#        unidades del pedido.
# RN-04: todo pedido requiere ficha técnica completa antes de producción.
# (RN-03, estado del pedido, vive en Pedido.validar_modificable)
# ─────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field, field_validator

ESTADO_FICHA_COMPLETA = "COMPLETA"
ESTADO_FICHA_INCOMPLETA = "INCOMPLETA"


# ── Schema de ENTRADA (body del POST) ─────────────────────────
class FichaTecnicaCreate(BaseModel):
    tallas: list[str] = Field(..., min_length=1, description="Talla de cada prenda")
    dorsales: list[int] = Field(..., min_length=1, description="Dorsal de cada prenda")
    nombres: list[str] = Field(..., min_length=1, description="Nombre estampado de cada prenda")

    @field_validator("tallas")
    @classmethod
    def tallas_validas(cls, v: list[str]) -> list[str]:
        limpias = [t.strip().upper() for t in v]
        if any(not t for t in limpias):
            raise ValueError("El campo tallas no puede contener valores vacíos")
        return limpias

    @field_validator("nombres")
    @classmethod
    def nombres_validos(cls, v: list[str]) -> list[str]:
        limpios = [n.strip().upper() for n in v]
        if any(not n for n in limpios):
            raise ValueError("El campo nombres no puede contener valores vacíos")
        return limpios

    @field_validator("dorsales")
    @classmethod
    def dorsales_validos(cls, v: list[int]) -> list[int]:
        if any(d < 0 or d > 99 for d in v):
            raise ValueError("Los dorsales deben estar entre 0 y 99")
        return v


# ── Schema de SALIDA (data del JSON) ──────────────────────────
class FichaTecnicaResponse(BaseModel):
    idPedido: int
    idFichaTecnica: int
    totalPrendas: int
    estadoFicha: str


# ── Entidad: ficha técnica ────────────────────────────────────
class FichaTecnica:
    def __init__(self, id: int, id_pedido: int, tallas: list[str],
                 dorsales: list[int], nombres: list[str]):
        self.id = id
        self.id_pedido = id_pedido
        self.tallas = tallas
        self.dorsales = dorsales
        self.nombres = nombres

    def unidades_recibidas(self) -> int:
        # Si las tres listas difieren entre sí, se reporta la más corta
        return min(len(self.tallas), len(self.dorsales), len(self.nombres))

    # RN-08: tallas, dorsales y nombres deben coincidir con las unidades del pedido
    def validar_consistencia(self, unidades_pedido: int) -> None:
        if not (len(self.tallas) == len(self.dorsales)
                == len(self.nombres) == unidades_pedido):
            raise ValueError(
                "La cantidad de tallas y dorsales no coincide con el número "
                "de unidades del pedido"
            )

    # RN-04: la ficha está completa si cada prenda tiene talla, dorsal y nombre
    def esta_completa(self) -> bool:
        return (
            len(self.tallas) > 0
            and len(self.tallas) == len(self.dorsales) == len(self.nombres)
            and all(t.strip() for t in self.tallas)
            and all(n.strip() for n in self.nombres)
        )

    def estado(self) -> str:
        return ESTADO_FICHA_COMPLETA if self.esta_completa() else ESTADO_FICHA_INCOMPLETA

    def to_response(self) -> dict:
        return {
            "idPedido": self.id_pedido,
            "idFichaTecnica": self.id,
            "totalPrendas": len(self.tallas),
            "estadoFicha": self.estado(),
        }