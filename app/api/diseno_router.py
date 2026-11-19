from fastapi import APIRouter, status

from app.core.responses import RespuestaApi
from app.domain.diseno import (
    DisenoAprobacionResponse, DisenoDecisionRequest, DisenoResolucionResponse,
)
from app.repositories.diseno_repo import diseno_repository
from app.services.diseno_service import DisenoService

router = APIRouter(prefix="/api/disenos", tags=["Diseños"])
service = DisenoService(repo=diseno_repository)


@router.post(
    "/{id}/aprobacion",
    response_model=RespuestaApi[DisenoAprobacionResponse],
    status_code=status.HTTP_201_CREATED,
)
def enviar_arte_a_aprobacion(id: int):
    """HU-018: envía el arte del pedido al cliente para su aprobación."""
    resultado = service.enviar_a_aprobacion(id)
    return {"mensaje": "Arte enviado a aprobación exitosamente", "data": resultado, "success": True}


@router.put(
    "/{id}/aprobacion",
    response_model=RespuestaApi[DisenoResolucionResponse],
    response_model_exclude_none=True,
)
def resolver_aprobacion_de_arte(id: int, datos: DisenoDecisionRequest):
    """HU-019 y HU-020: el cliente aprueba o rechaza el arte."""
    resultado = service.resolver_aprobacion(id, datos)
    return {"mensaje": "Arte aprobado exitosamente", "data": resultado, "success": True}
