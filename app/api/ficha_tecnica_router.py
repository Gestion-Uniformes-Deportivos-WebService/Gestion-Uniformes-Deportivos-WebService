# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP. Solo recibe peticiones y llama al servicio.
# Los errores los convierte app/core/manejadores.py
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Path, status

from app.core.respuesta import RespuestaApi, respuesta_ok
from app.domain.ficha_tecnica import FichaTecnicaCreate, FichaTecnicaResponse
from app.repositories.ficha_tecnica_repository import ficha_tecnica_repository
from app.repositories.pedido_repository import pedido_repository
from app.services.ficha_tecnica_service import FichaTecnicaService

router = APIRouter(prefix="/api/pedidos", tags=["Ficha técnica (MOD-01)"])

service = FichaTecnicaService(repo=ficha_tecnica_repository,
                              pedidos=pedido_repository)


# ── POST /api/pedidos/{id}/ficha-tecnica — HU-004 ─────────────
@router.post(
    "/{id}/ficha-tecnica",
    response_model=RespuestaApi[FichaTecnicaResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Datos de entrada inválidos"},
        422: {"description": "Regla de negocio incumplida (RN-08, RN-04, RN-03)"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def registrar_ficha_tecnica(
    datos: FichaTecnicaCreate,
    id: str = Path(..., description="ID del pedido"),
):
    """Registra la planilla de tallas, dorsales y nombres del pedido."""
    creada = service.registrar(id, datos)
    return respuesta_ok("Ficha técnica registrada exitosamente", creada)