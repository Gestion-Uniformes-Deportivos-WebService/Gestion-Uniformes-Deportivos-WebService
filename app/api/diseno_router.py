from fastapi import APIRouter, status

from app.core.responses import RespuestaApi
from app.domain.diseno import DisenoAprobacionResponse
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