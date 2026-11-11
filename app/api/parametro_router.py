# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP. Solo recibe peticiones y llama al servicio.
# Los errores los convierte app/core/manejadores.py
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, status

from app.core.respuesta import RespuestaApi, respuesta_ok
from app.domain.parametro import ParametroCreate, ParametroResponse
from app.repositories.parametro_repository import parametro_repository
from app.service.parametro_service import ParametroService

router = APIRouter(prefix="/api/parametros", tags=["Parámetros (MOD-08)"])

service = ParametroService(repo=parametro_repository)


# ── POST /api/parametros — HU-033 ─────────────────────────────
@router.post(
    "",
    response_model=RespuestaApi[ParametroResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Datos de entrada inválidos"},
        409: {"description": "Parámetro duplicado (RN-46) o valor inválido (RN-47)"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def registrar_parametro(datos: ParametroCreate):
    """Registra un parámetro de configuración asociado a un módulo."""
    creado = service.registrar(datos)
    return respuesta_ok("Parámetro registrado exitosamente", creado)
