from datetime import date
from typing import Optional
from app.domain.produccion import EstadoOrden, LineaProduccion, OrdenProduccion


class ProduccionRepository:

    def __init__(self):
        self._lineas = {
            "LINEA-01": LineaProduccion("LINEA-01", 100),
            "LINEA-02": LineaProduccion("LINEA-02", 100),
        }
        self._ordenes: dict[int, OrdenProduccion] = {}
        self._siguiente_id = 412
        self._seed()

    def _seed(self):
        iniciales = [
            OrdenProduccion(410, 1020, "LINEA-01", date(2026, 11, 2), date(2026, 11, 13),
                            24, EstadoOrden.EN_PRODUCCION, prendas_terminadas=24),
            OrdenProduccion(411, 1021, "LINEA-01", date(2026, 11, 2), date(2026, 11, 13),
                            12, EstadoOrden.EN_PRODUCCION, prendas_terminadas=0),
        ]
        self._ordenes = {o.id: o for o in iniciales}

    def obtener_linea(self, nombre: str) -> Optional[LineaProduccion]:
        return self._lineas.get(nombre)

    def obtener_por_id(self, id: int) -> Optional[OrdenProduccion]:
        return self._ordenes.get(id)

    def obtener_por_pedido(self, id_pedido: int) -> Optional[OrdenProduccion]:
        return next((o for o in self._ordenes.values() if o.id_pedido == id_pedido), None)

    def ordenes_de_linea_solapadas(self, linea: str, inicio: date, fin: date) -> list[OrdenProduccion]:
        return [o for o in self._ordenes.values()
                if o.linea == linea and o.solapa_con(inicio, fin)]

    def crear(self, id_pedido: int, linea: str, inicio: date, fin: date,
              cantidad: int) -> OrdenProduccion:
        orden = OrdenProduccion(self._siguiente_id, id_pedido, linea, inicio, fin, cantidad)
        self._ordenes[orden.id] = orden
        self._siguiente_id += 1
        return orden


produccion_repository = ProduccionRepository()