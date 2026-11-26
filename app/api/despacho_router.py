from fastapi import APIRouter, Path, status

from app.core.responses import RespuestaApi
from app.domain.despacho import (
    ConfirmarEntregaRequest, DespachoRequest, DespachoResponse,
    EntregaResponse, VerificacionResponse,
)
from app.repositories.despacho_repo import despacho_repository
from app.repositories.pedido_despacho_stub_repo import pedido_despacho_stub_repository
from app.services.despacho_service import DespachoService

router = APIRouter(prefix="/api/despachos", tags=["Despachos"])
service = DespachoService(repo=despacho_repository, pedido_repo=pedido_despacho_stub_repository)


@router.post(
    "",
    response_model=RespuestaApi[DespachoResponse],
    status_code=status.HTTP_201_CREATED,
)
def generar_guia_de_despacho(datos: DespachoRequest):
    """HU-029: genera la guía de envío de un pedido pagado y completo."""
    resultado = service.generar_guia(datos)
    return {"mensaje": "Guía de despacho generada exitosamente", "data": resultado, "success": True}


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


@router.put(
    "/{guia}/entrega",
    response_model=RespuestaApi[EntregaResponse],
)
def confirmar_entrega_del_pedido(
    datos: ConfirmarEntregaRequest,
    guia: str = Path(..., pattern=r"^GU-\d{4}-\d{4}$"),
):
    """HU-032: registra la recepción del pedido por parte del cliente."""
    resultado = service.confirmar_entrega(guia, datos)
    return {"mensaje": "Entrega confirmada exitosamente", "data": resultado, "success": True}