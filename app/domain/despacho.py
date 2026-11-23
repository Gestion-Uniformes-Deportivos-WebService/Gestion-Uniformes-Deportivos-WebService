from typing import Optional
from pydantic import BaseModel

from app.domain.errores import ReglaNegocioError


class ItemEmpaque:
    def __init__(self, referencia: str, cantidad_orden: int, cantidad_empacada: int):
        self.referencia = referencia
        self.cantidad_orden = cantidad_orden
        self.cantidad_empacada = cantidad_empacada

    def faltante(self) -> int:
        return max(self.cantidad_orden - self.cantidad_empacada, 0)


class Empaque:
    """Lo empacado de un pedido, para contrastarlo con la orden."""

    def __init__(self, id_pedido: int, items: list[ItemEmpaque],
                 no_conformidades_abiertas: int = 0, estado: str = "EN_EMPAQUE"):
        self.id_pedido = id_pedido
        self.items = items
        self.no_conformidades_abiertas = no_conformidades_abiertas
        self.estado = estado

    def prendas_orden(self) -> int:
        return sum(i.cantidad_orden for i in self.items)

    def prendas_empacadas(self) -> int:
        return sum(i.cantidad_empacada for i in self.items)

    def faltantes(self) -> list[dict]:
        return [{"referencia": i.referencia, "cantidad": i.faltante()}
                for i in self.items if i.faltante() > 0]

    def esta_completo(self) -> bool:
        # RN-39: el empaque debe coincidir con la orden
        return not self.faltantes()

    def validar_sin_no_conformidades(self) -> None:
        # RN-29: una prenda con no conformidad no se despacha hasta cerrar el reproceso
        if self.no_conformidades_abiertas > 0:
            raise ReglaNegocioError(
                "El pedido tiene prendas con no conformidad pendiente de reproceso",
                {"idPedido": self.id_pedido,
                 "noConformidadesAbiertas": self.no_conformidades_abiertas},
            )

    def marcar_listo_para_despacho(self) -> None:
        self.estado = "LISTO_PARA_DESPACHO"


class FaltanteItem(BaseModel):
    referencia: str
    cantidad: int


class VerificacionResponse(BaseModel):
    idPedido: int
    prendasOrden: int
    prendasEmpacadas: int
    completo: bool
    estado: Optional[str] = None
    faltantes: Optional[list[FaltanteItem]] = None