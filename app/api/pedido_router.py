# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP. Solo recibe peticiones y llama al servicio.
# Los errores los convierte app/core/manejadores.py
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, status

from app.core.respuesta import RespuestaApi, respuesta_ok
from app.domain.pedido import PedidoCreate, PedidoResponse
from app.repositories.cliente_repository import cliente_repository
from app.repositories.parametro_repository import parametro_repository
from app.repositories.pedido_repository import pedido_repository
from app.services.pedido_service import PedidoService

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos (MOD-01)"])

service = PedidoService(
    repo=pedido_repository,
    clientes=cliente_repository,
    parametros=parametro_repository,
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