from fastapi import APIRouter, status

from app.core.responses import RespuestaApi
from app.domain.produccion import OrdenProduccionRequest, OrdenProduccionResponse
from app.repositories.diseno_repo import diseno_repository
from app.repositories.inventario_repo import inventario_repository
from app.repositories.pedido_stub_repo import pedido_stub_repository
from app.repositories.produccion_repo import produccion_repository
from app.services.produccion_service import ProduccionService

router = APIRouter(prefix="/api/produccion", tags=["Producción"])
service = ProduccionService(
    repo=produccion_repository,
    pedido_repo=pedido_stub_repository,
    diseno_repo=diseno_repository,
    inventario_repo=inventario_repository,
)


@router.post(
    "/ordenes",
    response_model=RespuestaApi[OrdenProduccionResponse],
    status_code=status.HTTP_201_CREATED,
)
def programar_orden_de_produccion(datos: OrdenProduccionRequest):
    """HU-021: asigna fecha y línea de producción a un pedido."""
    resultado = service.programar_orden(datos)
    return {"mensaje": "Orden de producción programada exitosamente", "data": resultado, "success": True}