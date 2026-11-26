# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP. Solo recibe peticiones y llama al servicio.
# Los errores los convierte app/core/manejadores.py
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, status

from app.core.respuesta import RespuestaApi, respuesta_ok
from app.domain.parametro import ParametroCreate, ParametroResponse, ParametrosModuloResponse
from app.repositories.parametro_repository import parametro_repository
from app.services.parametro_service import ParametroService
from fastapi import APIRouter, Query, status

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


# ── GET /api/parametros?modulo=MOD-01 — HU-035 ────────────────
@router.get(
    "",
    response_model=RespuestaApi[ParametrosModuloResponse],
    responses={
        400: {"description": "Código de módulo inválido"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def consultar_parametros(
    modulo: str = Query(..., description="Código del módulo (MOD-NN)"),
):
    """Lista los parámetros configurados para un módulo."""
    resultado = service.consultar_por_modulo(modulo)
    return respuesta_ok("Consulta de parámetros exitosa", resultado)