# ─────────────────────────────────────────────────────────────
# CAPA REPOSITORIO — almacenamiento en memoria de pedidos
# Solo guarda y recupera. Sin lógica de negocio.
# ─────────────────────────────────────────────────────────────

from typing import Optional

from app.domain.pedido import EsquemaDePago, Pedido


class PedidoRepository:

    def __init__(self):
        self._datos: list[Pedido] = []
        # Los ids de pedido arrancan en 1024 (el primer pedido recibe ese id)
        self._siguiente_id: int = 1024

    def obtener_todos(self) -> list[Pedido]:
        return self._datos.copy()

    def obtener_por_id(self, id: int) -> Optional[Pedido]:
        return next((p for p in self._datos if p.id == id), None)

    def crear(self, id_cliente: int, prendas: list[dict], cantidad: int,
              estado: str, esquema_pago: EsquemaDePago) -> Pedido:
        nuevo = Pedido(self._siguiente_id, id_cliente, prendas,
                       cantidad, estado, esquema_pago)
        self._datos.append(nuevo)
        self._siguiente_id += 1
        return nuevo


# Instancia única compartida (Singleton simple)
pedido_repository = PedidoRepository()