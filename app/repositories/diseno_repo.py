from typing import Optional
from app.domain.diseno import Diseno, EstadoDiseno


class DisenoRepository:

    def __init__(self):
        self._datos: dict[int, Diseno] = {}
        self._seed()

    def _seed(self):
        iniciales = [
            Diseno(205, 1024, "arte_halcones_v1.png"),                       # caso exitoso
            Diseno(206, 1025, None),                                          # sin archivo
            Diseno(207, 1030, "arte_tigres_v2.png"),                          # pedido con otro pendiente
            Diseno(208, 1030, "arte_tigres_v1.png", EstadoDiseno.PENDIENTE_APROBACION),
        ]
        self._datos = {d.id: d for d in iniciales}

    def obtener_por_id(self, id: int) -> Optional[Diseno]:
        return self._datos.get(id)

    def obtener_pendiente_por_pedido(self, id_pedido: int) -> Optional[Diseno]:
        return next(
            (d for d in self._datos.values()
             if d.id_pedido == id_pedido and d.estado == EstadoDiseno.PENDIENTE_APROBACION),
            None,
        )

    def guardar(self, diseno: Diseno) -> Diseno:
        self._datos[diseno.id] = diseno
        return diseno


# Instancia única compartida (la usarán también HU-019 y HU-020)
diseno_repository = DisenoRepository()