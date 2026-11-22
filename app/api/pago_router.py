# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP. Solo recibe peticiones y llama al servicio.
# Los errores los convierte app/core/manejadores.py
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, status

from app.domain.pago import (
    PagoAnticipoCreate,
    PagoResponse,
    PagoSaldoCreate,
    PagoSaldoResponse,
)
from app.core.respuesta import RespuestaApi, respuesta_ok
from app.repositories.cliente_repository import cliente_repository
from app.repositories.pago_repository import pago_repository
from app.repositories.parametro_repository import parametro_repository
from app.repositories.pedido_repository import pedido_repository
from app.services.pago_service import PagoService
from app.services.pedido_service import PedidoService

router = APIRouter(prefix="/api/pagos", tags=["Pagos (MOD-03)"])

service = PagoService(
    repo=pago_repository,
    pedidos=pedido_repository,
    pedido_service=PedidoService(
        repo=pedido_repository,
        clientes=cliente_repository,
        parametros=parametro_repository,
        pagos=pago_repository,
    ),
)


# ── POST /api/pagos/anticipo — HU-011 ─────────────────────────
@router.post(
    "/anticipo",
    response_model=RespuestaApi[PagoResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Datos de entrada inválidos (ej. monto <= 0)"},
        422: {"description": "Regla incumplida (RN-17, RN-20), comprobante repetido o pedido inexistente"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def registrar_anticipo(datos: PagoAnticipoCreate):
    """Registra un abono al anticipo (50%) del pedido. Los abonos se acumulan."""
    pago, mensaje = service.registrar_anticipo(datos)
    return respuesta_ok(mensaje, pago)

# ── POST /api/pagos/saldo — HU-012 ────────────────────────────
@router.post(
    "/saldo",
    response_model=RespuestaApi[PagoSaldoResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Datos de entrada inválidos"},
                422: {"description": "El monto supera lo pendiente, pedido inexistente o ya pagado"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def registrar_saldo(datos: PagoSaldoCreate):
    """Registra el saldo del pedido. Admite abonos parciales sin superar lo pendiente."""
    pago, mensaje = service.registrar_saldo(datos)
    return respuesta_ok(mensaje, pago)