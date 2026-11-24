from datetime import date
from typing import Optional
from app.domain.despacho import Despacho, Empaque, ItemEmpaque, Transportadora


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


# Instancia única compartida
despacho_repository = DespachoRepository()