from fastapi import APIRouter, status

from app.core.responses import RespuestaApi
from app.domain.produccion import InspeccionRequest, InspeccionResponse
from app.repositories.calidad_repo import calidad_repository
from app.repositories.produccion_repo import produccion_repository
from app.services.calidad_service import CalidadService

router = APIRouter(prefix="/api/produccion", tags=["Calidad"])
service = CalidadService(calidad_repo=calidad_repository, produccion_repo=produccion_repository)


@router.post(
    "/calidad",
    response_model=RespuestaApi[InspeccionResponse],
    status_code=status.HTTP_201_CREATED,
)
def registrar_inspeccion_de_calidad(datos: InspeccionRequest):
    """HU-023: registra el resultado de la inspección de un lote terminado."""
    resultado = service.registrar_inspeccion(datos)
    return {"mensaje": "Inspección de calidad registrada exitosamente", "data": resultado, "success": True}