
from datetime import date
from typing import Optional

from app.domain.despacho import (
    Despacho,
    Empaque,
    EstadoDespacho,
    ItemEmpaque,
    Transportadora,
)


class DespachoRepository:

    def __init__(self):
        self._empaques: dict[int, Empaque] = {}
        self._transportadoras: dict[str, Transportadora] = {}
        self._despachos: dict[str, Despacho] = {}

        self._siguiente_id = 15
        self._siguiente_guia = 1

        self._seed()

    def _seed(self):

        # HU-030: Empaques de ejemplo
        empaques = [
            # Pedido completo
            Empaque(
                1024,
                [
                    ItemEmpaque("Camiseta M", 12, 12),
                    ItemEmpaque("Short M", 12, 12)
                ]
            ),

            # Pedido con faltantes
            Empaque(
                1026,
                [
                    ItemEmpaque("Camiseta M #7", 12, 11),
                    ItemEmpaque("Short L #10", 12, 11)
                ]
            ),

            # Pedido con una no conformidad abierta
            Empaque(
                1027,
                [ItemEmpaque("Camiseta L", 12, 12)],
                no_conformidades_abiertas=1
            ),

            # Pedidos completos para probar la guía
            Empaque(
                1028,
                [ItemEmpaque("Camiseta S", 12, 12)]
            ),

            Empaque(
                1030,
                [ItemEmpaque("Camiseta XL", 12, 12)]
            ),
        ]

        self._empaques = {
            e.id_pedido: e for e in empaques
        }

        # HU-029: Transportadoras de ejemplo
        transportadoras = [
            Transportadora(
                "Transportadora Andina",
                {"SANTANDER", "BOGOTA", "ANTIOQUIA"}
            ),

            Transportadora(
                "Envios Costa",
                {"ATLANTICO", "BOLIVAR"}
            ),
        ]

        self._transportadoras = {
            t.nombre: t for t in transportadoras
        }

        # HU-032: Despachos de ejemplo
        despachos = [
            # Guía pendiente de entrega
            Despacho(
                10,
                1050,
                "Transportadora Andina",
                "GU-2026-0100"
            ),

            # Guía que ya fue entregada
            Despacho(
                11,
                1051,
                "Envios Costa",
                "GU-2026-0101",
                EstadoDespacho.ENTREGADO,
                date(2026, 11, 5),
                "Ana Gómez"
            ),
        ]

        self._despachos = {
            d.guia: d for d in despachos
        }

    # ==========================================
    # HU-030: EMPAQUES
    # ==========================================

    def obtener_por_pedido(
        self,
        id_pedido: int
    ) -> Optional[Empaque]:
        return self._empaques.get(id_pedido)

    def guardar(self, empaque: Empaque) -> Empaque:
        self._empaques[empaque.id_pedido] = empaque
        return empaque

    # ==========================================
    # HU-029: TRANSPORTADORAS Y GUÍAS
    # ==========================================

    def obtener_transportadora(
        self,
        nombre: str
    ) -> Optional[Transportadora]:
        return self._transportadoras.get(nombre)

    def obtener_despacho_por_pedido(
        self,
        id_pedido: int
    ) -> Optional[Despacho]:
        return next(
            (
                d for d in self._despachos.values()
                if d.id_pedido == id_pedido
            ),
            None
        )

    def crear_despacho(
        self,
        id_pedido: int,
        transportadora: str
    ) -> Despacho:

        guia = (
            f"GU-{date.today().year}-"
            f"{self._siguiente_guia:04d}"
        )

        despacho = Despacho(
            self._siguiente_id,
            id_pedido,
            transportadora,
            guia
        )

        self._despachos[guia] = despacho

        self._siguiente_id += 1
        self._siguiente_guia += 1

        return despacho

    # ==========================================
    # HU-032: CONFIRMAR ENTREGA
    # ==========================================

    def obtener_despacho_por_guia(
        self,
        guia: str
    ) -> Optional[Despacho]:
        return self._despachos.get(guia)

    def guardar_despacho(
        self,
        despacho: Despacho
    ) -> Despacho:
        self._despachos[despacho.guia] = despacho
        return despacho


# ==========================================
# INSTANCIA ÚNICA COMPARTIDA
# ==========================================

despacho_repository = DespachoRepository()

