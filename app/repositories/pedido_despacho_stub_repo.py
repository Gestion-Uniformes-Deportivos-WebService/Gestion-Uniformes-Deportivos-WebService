from typing import Optional
from app.domain.despacho import PedidoDespacho


class PedidoDespachoStubRepository:
    """Simula los datos de pago y destino de un pedido (módulos de tu compañero)."""

    def __init__(self):
        iniciales = [
            PedidoDespacho(1024, 0, "SANTANDER"),        # pagado, destino Santander
            PedidoDespacho(1026, 0, "SANTANDER"),        # pagado (empaque con faltantes)
            PedidoDespacho(1027, 0, "SANTANDER"),        # pagado (no conformidad abierta)
            PedidoDespacho(1028, 540000, "SANTANDER"),   # saldo pendiente
            PedidoDespacho(1030, 0, "ATLANTICO"),        # pagado, destino Atlántico
        ]
        self._datos = {p.id: p for p in iniciales}

    def obtener_por_id(self, id: int) -> Optional[PedidoDespacho]:
        return self._datos.get(id)


pedido_despacho_stub_repository = PedidoDespachoStubRepository()