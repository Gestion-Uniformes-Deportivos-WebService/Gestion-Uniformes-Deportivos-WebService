from typing import Optional
from app.domain.inventario import Insumo, MovimientoInventario, TipoMovimiento


class InventarioRepository:

    def __init__(self):
        self._insumos: dict[str, Insumo] = {}
        self._movimientos: list[MovimientoInventario] = []
        self._siguiente_id = 3300
        self._seed()

    def _seed(self):
        iniciales = [
            Insumo("tela-dryfit-azul", 25),
            Insumo("hilo-poliester", 40),
            Insumo("tinta-sublimacion", 0),
        ]
        self._insumos = {i.nombre: i for i in iniciales}

    def obtener_insumo(self, nombre: str) -> Optional[Insumo]:
        return self._insumos.get(nombre)

    def registrar_movimiento(self, insumo: Insumo, tipo: TipoMovimiento,
                             cantidad: int) -> MovimientoInventario:
        mov = MovimientoInventario(self._siguiente_id, insumo.nombre, tipo,
                                   cantidad, insumo.stock)
        self._movimientos.append(mov)
        self._siguiente_id += 1
        return mov


inventario_repository = InventarioRepository()