from typing import Optional
from app.domain.despacho import Empaque, ItemEmpaque


class DespachoRepository:

    def __init__(self):
        self._empaques: dict[int, Empaque] = {}
        self._seed()

    def _seed(self):
        iniciales = [
            # Pedido completo
            Empaque(1024, [ItemEmpaque("Camiseta M", 12, 12), ItemEmpaque("Short M", 12, 12)]),
            # Pedido con faltantes
            Empaque(1026, [ItemEmpaque("Camiseta M #7", 12, 11), ItemEmpaque("Short L #10", 12, 11)]),
            # Pedido con una no conformidad abierta
            Empaque(1027, [ItemEmpaque("Camiseta L", 12, 12)], no_conformidades_abiertas=1),
        ]
        self._empaques = {e.id_pedido: e for e in iniciales}

    def obtener_por_pedido(self, id_pedido: int) -> Optional[Empaque]:
        return self._empaques.get(id_pedido)

    def guardar(self, empaque: Empaque) -> Empaque:
        self._empaques[empaque.id_pedido] = empaque
        return empaque


# Instancia única compartida
despacho_repository = DespachoRepository()