from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from app.domain.errores import ReglaNegocioError, ValidacionDominioError


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

    def validar_completo(self) -> None:
        # RN-42: un pedido con faltantes no pasa a despacho
        if not self.esta_completo():
            raise ReglaNegocioError(
                "No se puede generar la guía: el pedido tiene faltantes",
                {"idPedido": self.id_pedido, "faltantes": self.faltantes()},
            )

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


class PedidoDespacho:
    """Datos del pedido necesarios para despachar (simulados hasta integrar los módulos de pedidos y pagos)."""

    def __init__(self, id: int, saldo_pendiente: int, zona_destino: str):
        self.id = id
        self.saldo_pendiente = saldo_pendiente
        self.zona_destino = zona_destino

    def validar_paz_y_salvo(self) -> None:
        # RN-38 y RN-16: no se genera guía sin el saldo final pagado
        if self.saldo_pendiente > 0:
            raise ReglaNegocioError(
                "No se puede generar la guía: el pedido no tiene el saldo final pagado",
                {"idPedido": self.id, "saldoPendiente": self.saldo_pendiente},
            )


class Transportadora:
    def __init__(self, nombre: str, zonas: set[str], activa: bool = True):
        self.nombre = nombre
        self.zonas = zonas
        self.activa = activa

    def validar_para_zona(self, zona: str) -> None:
        # RN-40: solo se usa una transportadora habilitada para la zona de destino
        if not self.activa or zona not in self.zonas:
            raise ValidacionDominioError(
                "La transportadora no está habilitada para la zona de destino",
                {"transportadora": self.nombre, "zonaDestino": zona},
            )


class EstadoDespacho(str, Enum):
    GUIA_GENERADA = "GUIA_GENERADA"
    ENTREGADO = "ENTREGADO"


class Despacho:
    def __init__(self, id: int, id_pedido: int, transportadora: str, guia: str,
                 estado: EstadoDespacho = EstadoDespacho.GUIA_GENERADA):
        self.id = id
        self.id_pedido = id_pedido
        self.transportadora = transportadora
        self.guia = guia
        self.estado = estado


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


class DespachoRequest(BaseModel):
    idPedido: int
    transportadora: str = Field(..., min_length=1)


class DespachoResponse(BaseModel):
    idDespacho: int
    idPedido: int
    transportadora: str
    guia: str
    estado: EstadoDespacho