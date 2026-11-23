# ─────────────────────────────────────────────────────────────
# CAPA REPOSITORIO — almacenamiento en memoria de pagos
# Solo guarda y recupera. Sin lógica de negocio.
# ─────────────────────────────────────────────────────────────

from app.domain.pago import Pago


class PagoRepository:

    def __init__(self):
        self._datos: list[Pago] = []
        # Los ids de pago arrancan en 3001 (el primer pago recibe ese id)
        self._siguiente_id: int = 3001

    def obtener_por_pedido(self, id_pedido: int) -> list[Pago]:
        return [p for p in self._datos if p.id_pedido == id_pedido]

    def total_pagado(self, id_pedido: int) -> int:
        """Suma de todos los abonos registrados del pedido."""
        return sum(p.monto for p in self._datos if p.id_pedido == id_pedido)

    def existe_comprobante(self, comprobante: str) -> bool:
        """¿Ya se registró este comprobante? (sin distinguir mayúsculas)"""
        buscado = comprobante.strip().lower()
        return any(p.comprobante.lower() == buscado for p in self._datos)

    def crear(self, id_pedido: int, monto: int, tipo: str,
              comprobante: str, estado: str) -> Pago:
        nuevo = Pago(self._siguiente_id, id_pedido, monto, tipo, comprobante, estado)
        self._datos.append(nuevo)
        self._siguiente_id += 1
        return nuevo


# Instancia única compartida (Singleton simple)
pago_repository = PagoRepository()