from app.domain.produccion import InspeccionCalidad, ResultadoInspeccion


class CalidadRepository:

    def __init__(self):
        self._inspecciones: list[InspeccionCalidad] = []
        self._siguiente_id = 950

    def registrar(self, id_orden: int, resultado: ResultadoInspeccion,
                  prendas: int) -> InspeccionCalidad:
        inspeccion = InspeccionCalidad(self._siguiente_id, id_orden, resultado, prendas)
        self._inspecciones.append(inspeccion)
        self._siguiente_id += 1
        return inspeccion


calidad_repository = CalidadRepository()