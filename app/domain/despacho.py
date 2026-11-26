from datetime import date
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
                 estado: EstadoDespacho = EstadoDespacho.GUIA_GENERADA,
                 fecha_entrega: Optional[date] = None,
                 firma: Optional[str] = None):
        self.id = id
        self.id_pedido = id_pedido
        self.transportadora = transportadora
        self.guia = guia
        self.estado = estado
        self.fecha_entrega = fecha_entrega
        self.firma = firma

    def confirmar_entrega(self, fecha: date, firma: Optional[str]) -> None:
        # RN-06: el estado solo avanza en secuencia; un despacho entregado no se vuelve a entregar
        if self.estado == EstadoDespacho.ENTREGADO:
            raise ReglaNegocioError(
                "El despacho ya fue entregado",
                {"guia": self.guia,
                 "fechaEntrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None},
            )
        # RN-41: no se confirma ENTREGADO sin fecha y firma de recepción
        if not firma or not firma.strip():
            raise ValidacionDominioError(
                "No se puede confirmar la entrega sin fecha y firma de recepción",
                {"guia": self.guia},
            )
        self.estado = EstadoDespacho.ENTREGADO
        self.fecha_entrega = fecha
        self.firma = firma.strip()


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


class ConfirmarEntregaRequest(BaseModel):
    fecha: date
    firma: Optional[str] = None

from datetime import date
from typing import Optional
from app.domain.despacho import (
    Despacho, Empaque, EstadoDespacho, ItemEmpaque, Transportadora,
)


class DespachoRepository:

    def __init__(self):
        self._empaques: dict[int, Empaque] = {}
        self._transportadoras: dict[str, Transportadora] = {}
        self._despachos: dict[str, Despacho] = {}   # clave: número de guía
        self._siguiente_id = 15
        self._siguiente_guia = 1
        self._seed()

    def _seed(self):
        empaques = [
            # Pedido completo
            Empaque(1024, [ItemEmpaque("Camiseta M", 12, 12), ItemEmpaque("Short M", 12, 12)]),
            # Pedido con faltantes
            Empaque(1026, [ItemEmpaque("Camiseta M #7", 12, 11), ItemEmpaque("Short L #10", 12, 11)]),
            # Pedido con una no conformidad abierta
            Empaque(1027, [ItemEmpaque("Camiseta L", 12, 12)], no_conformidades_abiertas=1),
            # Pedidos completos para probar la guía
            Empaque(1028, [ItemEmpaque("Camiseta S", 12, 12)]),
            Empaque(1030, [ItemEmpaque("Camiseta XL", 12, 12)]),
        ]
        self._empaques = {e.id_pedido: e for e in empaques}

        transportadoras = [
            Transportadora("Transportadora Andina", {"SANTANDER", "BOGOTA", "ANTIOQUIA"}),
            Transportadora("Envios Costa", {"ATLANTICO", "BOLIVAR"}),
        ]
        self._transportadoras = {t.nombre: t for t in transportadoras}

        # Despachos de ejemplo para probar la confirmación de entrega
        despachos = [
            Despacho(10, 1050, "Transportadora Andina", "GU-2026-0100"),
            Despacho(11, 1051, "Envios Costa", "GU-2026-0101",
                     EstadoDespacho.ENTREGADO, date(2026, 11, 5), "Ana Gómez"),
        ]
        self._despachos = {d.guia: d for d in despachos}

    # ---- empaque (HU-030)
    def obtener_por_pedido(self, id_pedido: int) -> Optional[Empaque]:
        return self._empaques.get(id_pedido)

    def guardar(self, empaque: Empaque) -> Empaque:
        self._empaques[empaque.id_pedido] = empaque
        return empaque

    # ---- transportadoras y guías (HU-029)
    def obtener_transportadora(self, nombre: str) -> Optional[Transportadora]:
        return self._transportadoras.get(nombre)

    def obtener_despacho_por_pedido(self, id_pedido: int) -> Optional[Despacho]:
        return next((d for d in self._despachos.values() if d.id_pedido == id_pedido), None)

    def crear_despacho(self, id_pedido: int, transportadora: str) -> Despacho:
        guia = f"GU-{date.today().year}-{self._siguiente_guia:04d}"
        despacho = Despacho(self._siguiente_id, id_pedido, transportadora, guia)
        self._despachos[guia] = despacho
        self._siguiente_id += 1
        self._siguiente_guia += 1
        return despacho

    # ---- entrega (HU-032)
    def obtener_despacho_por_guia(self, guia: str) -> Optional[Despacho]:
        return self._despachos.get(guia)

    def guardar_despacho(self, despacho: Despacho) -> Despacho:
        self._despachos[despacho.guia] = despacho
        return despacho


# Instancia única compartida
despacho_repository = DespachoRepository()
class EntregaResponse(BaseModel):
    guia: str
    idPedido: int
    fechaEntrega: date
    estado: EstadoDespacho