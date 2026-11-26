from app.domain.errores import RecursoNoEncontradoError
from app.domain.produccion import InspeccionRequest, InspeccionResponse
from app.repositories.calidad_repo import CalidadRepository
from app.repositories.produccion_repo import ProduccionRepository


class CalidadService:

    def __init__(self, calidad_repo: CalidadRepository, produccion_repo: ProduccionRepository):
        self.calidad_repo = calidad_repo
        self.produccion_repo = produccion_repo

    def registrar_inspeccion(self, datos: InspeccionRequest) -> InspeccionResponse:
        orden = self.produccion_repo.obtener_por_id(datos.idOrden)
        if not orden:
            raise RecursoNoEncontradoError(
                "La orden de producción no existe", {"idOrden": datos.idOrden}
            )

        orden.validar_lote_para_inspeccion()   # RN-28

        inspeccion = self.calidad_repo.registrar(
            orden.id, datos.resultado, orden.prendas_terminadas
        )
        return InspeccionResponse(
            idInspeccion=inspeccion.id, idOrden=inspeccion.id_orden,
            resultado=inspeccion.resultado,
            prendasInspeccionadas=inspeccion.prendas_inspeccionadas,
        )