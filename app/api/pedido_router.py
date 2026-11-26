# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP. Solo recibe peticiones y llama al servicio.
# Los errores los convierte app/core/manejadores.py
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Path, status

from app.domain.estado_pedido import (
    AutorizacionProduccionResponse,
    EstadoPedidoResponse,
    PedidoEstadoUpdate,
)
from app.repositories.diseno_repo import diseno_repository
from app.repositories.ficha_tecnica_repository import ficha_tecnica_repository
from app.services.autorizacion_produccion_service import AutorizacionProduccionService
from app.domain.pedido import CotizacionResponse, PedidoCreate, PedidoResponse
from app.core.respuesta import RespuestaApi, respuesta_ok
from app.repositories.cliente_repository import cliente_repository
from app.repositories.parametro_repository import parametro_repository
from app.repositories.pedido_repository import pedido_repository
from app.services.pedido_service import PedidoService
from app.repositories.pago_repository import pago_repository

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos (MOD-01)"])

service = PedidoService(
    repo=pedido_repository,
    clientes=cliente_repository,
    parametros=parametro_repository,
    pagos=pago_repository,
)

autorizacion_service = AutorizacionProduccionService(
    pedidos=pedido_repository,
    pagos=pago_repository,
    fichas=ficha_tecnica_repository,
    disenos=diseno_repository,
    pedido_service=service,
)


# ── POST /api/pedidos — HU-001 ────────────────────────────────
@router.post(
    "",
    response_model=RespuestaApi[PedidoResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Datos de entrada inválidos"},
        422: {"description": "Regla de negocio incumplida (RN-01, RN-02, RN-12, RN-14)"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def registrar_pedido(datos: PedidoCreate):
    """Registra y confirma un pedido de uniformes en estado PENDIENTE_ANTICIPO."""
    creado = service.registrar(datos)
    return respuesta_ok("Pedido registrado exitosamente", creado)

# ── GET /api/pedidos/{id}/cotizacion — HU-002 ─────────────────
@router.get(
    "/{id}/cotizacion",
    response_model=RespuestaApi[CotizacionResponse],
    responses={
        400: {"description": "Identificador de pedido no numérico"},
        404: {"description": "El pedido consultado no existe"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def cotizar_pedido(id: str = Path(..., description="ID del pedido a cotizar")):
    """Calcula el costo total del pedido con el desglose de anticipo (50%) y saldo (50%)."""
    cotizacion = service.cotizar(id)
    return respuesta_ok("Cotización calculada exitosamente", cotizacion)

# ── GET /api/pedidos/{id}/estado — HU-005 ─────────────────────
@router.get(
    "/{id}/estado",
    response_model=RespuestaApi[EstadoPedidoResponse],
    responses={
        400: {"description": "Identificador de pedido no numérico"},
        404: {"description": "El pedido consultado no existe"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def consultar_estado_pedido(id: str = Path(..., description="ID del pedido")):
    """Retorna la etapa actual del pedido: estado, pago, producción y despacho."""
    estado, mensaje = service.consultar_estado(id)
    return respuesta_ok(mensaje, estado)

# ── PUT /api/pedidos/{id}/estado — HU-003 ─────────────────────
@router.put(
    "/{id}/estado",
    response_model=RespuestaApi[AutorizacionProduccionResponse],
    responses={
        400: {"description": "Identificador o estado no válido"},
        409: {"description": "Regla incumplida (RN-06, RN-15, RN-04, RN-07)"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def autorizar_produccion(
    datos: PedidoEstadoUpdate,
    id: str = Path(..., description="ID del pedido"),
):
    """Autoriza el pase a producción del pedido y notifica al área de confección."""
    resultado = autorizacion_service.autorizar(id, datos)
    return respuesta_ok("Pedido autorizado para producción", resultado)