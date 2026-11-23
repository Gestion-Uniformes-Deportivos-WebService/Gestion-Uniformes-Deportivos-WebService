from fastapi import APIRouter

from app.core.responses import RespuestaApi
from app.domain.despacho import VerificacionResponse
from app.repositories.despacho_repo import despacho_repository
from app.services.despacho_service import DespachoService

router = APIRouter(prefix="/api/despachos", tags=["Despachos"])
service = DespachoService(repo=despacho_repository)


@router.get(
    "/{idPedido}/verificacion",
    response_model=RespuestaApi[VerificacionResponse],
    response_model_exclude_none=True,
)
def verificar_pedido_completo(idPedido: int):
    """HU-030: contrasta lo empacado con la orden original."""
    resultado = service.verificar_pedido(idPedido)
    if resultado.completo:
        return {"mensaje": "Pedido completo y listo para despacho",
                "data": resultado, "success": True}
    return {"mensaje": "El pedido tiene faltantes y no puede pasar a despacho",
            "data": resultado, "success": False}