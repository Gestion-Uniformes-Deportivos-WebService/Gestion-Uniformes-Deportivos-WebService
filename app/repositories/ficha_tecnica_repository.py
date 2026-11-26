# ─────────────────────────────────────────────────────────────
# CAPA REPOSITORIO — almacenamiento en memoria de fichas técnicas
# Solo guarda y recupera. Sin lógica de negocio.
# ─────────────────────────────────────────────────────────────

from typing import Optional

from app.domain.ficha_tecnica import FichaTecnica


class FichaTecnicaRepository:

    def __init__(self):
        self._datos: list[FichaTecnica] = []
        # Los ids de ficha arrancan en 501 (la primera ficha recibe ese id)
        self._siguiente_id: int = 501

    def obtener_por_pedido(self, id_pedido: int) -> Optional[FichaTecnica]:
        return next((f for f in self._datos if f.id_pedido == id_pedido), None)

    def guardar(self, id_pedido: int, tallas: list[str],
                dorsales: list[int], nombres: list[str]) -> FichaTecnica:
        """Crea la ficha del pedido; si ya existía, la reemplaza conservando su id."""
        existente = self.obtener_por_pedido(id_pedido)
        if existente:
            existente.tallas = tallas
            existente.dorsales = dorsales
            existente.nombres = nombres
            return existente

        nueva = FichaTecnica(self._siguiente_id, id_pedido, tallas, dorsales, nombres)
        self._datos.append(nueva)
        self._siguiente_id += 1
        return nueva


# Instancia única compartida (Singleton simple)
ficha_tecnica_repository = FichaTecnicaRepository()