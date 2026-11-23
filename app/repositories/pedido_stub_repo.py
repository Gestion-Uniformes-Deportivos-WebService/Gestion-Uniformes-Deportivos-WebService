from typing import Optional


class PedidoInfo:
    """Datos mínimos de un pedido. Simulados hasta integrar el módulo de pedidos."""

    def __init__(self, id: int, cantidad: int, ficha_completa: bool,
                 insumos_requeridos: dict[str, int]):
        self.id = id
        self.cantidad = cantidad
        self.ficha_completa = ficha_completa
        self.insumos_requeridos = insumos_requeridos


class PedidoStubRepository:

    def __init__(self):
        iniciales = [
            PedidoInfo(1024, 24, True, {"tela-dryfit-azul": 20, "hilo-poliester": 5}),
            PedidoInfo(1040, 24, True, {"tela-dryfit-azul": 20, "hilo-poliester": 5}),
            PedidoInfo(1041, 24, False, {"hilo-poliester": 5}),
            PedidoInfo(1042, 24, True, {"tinta-sublimacion": 10}),
            PedidoInfo(1043, 600, True, {"hilo-poliester": 5}),
        ]
        self._datos = {p.id: p for p in iniciales}

    def obtener_por_id(self, id: int) -> Optional[PedidoInfo]:
        return self._datos.get(id)


pedido_stub_repository = PedidoStubRepository()