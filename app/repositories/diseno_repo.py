from typing import Optional
from app.domain.diseno import Diseno, EstadoDiseno


class DisenoRepository:

    def __init__(self):
        self._datos: dict[int, Diseno] = {}
        self._seed()

    def _seed(self):
        aprobado = EstadoDiseno.DISENO_APROBADO
        iniciales = [
            Diseno(205, 1024, "arte_halcones_v1.png"),
            Diseno(206, 1025, None),
            Diseno(207, 1030, "arte_tigres_v2.png"),
            Diseno(208, 1030, "arte_tigres_v1.png", EstadoDiseno.PENDIENTE_APROBACION),
            # Diseños ya aprobados, para probar producción
            Diseno(209, 1040, "arte_leones.png", aprobado),
            Diseno(210, 1041, "arte_pumas.png", aprobado),
            Diseno(211, 1042, "arte_lobos.png", aprobado),
            Diseno(212, 1043, "arte_aguilas.png", aprobado),
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

    def tiene_diseno_aprobado(self, id_pedido: int) -> bool:
        return any(
            d.id_pedido == id_pedido and d.estado == EstadoDiseno.DISENO_APROBADO
            for d in self._datos.values()
        )

    def guardar(self, diseno: Diseno) -> Diseno:
        self._datos[diseno.id] = diseno
        return diseno


# Instancia única compartida
diseno_repository = DisenoRepository()