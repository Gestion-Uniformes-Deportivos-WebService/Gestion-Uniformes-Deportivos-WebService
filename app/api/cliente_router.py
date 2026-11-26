# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP. Solo recibe peticiones y llama al servicio.
# Los errores los convierte app/core/manejadores.py
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, status

from app.core.respuesta import RespuestaApi, respuesta_ok
from app.domain.cliente import ClienteCreate, ClienteResponse
from app.repositories.cliente_repository import cliente_repository
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/api/clientes", tags=["Clientes (MOD-02)"])

service = ClienteService(repo=cliente_repository)


# ── POST /api/clientes — HU-008 ───────────────────────────────
@router.post(
    "",
    response_model=RespuestaApi[ClienteResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Datos de entrada inválidos (ej. Documento/NIT no válido)"},
        409: {"description": "Ya existe un cliente activo con ese NIT (RN-10)"},
        503: {"description": "Falla del almacenamiento"},
    },
)
def registrar_cliente(datos: ClienteCreate):
    """Registra el perfil de un cliente (club, colegio o empresa)."""
    creado = service.registrar(datos)
    return respuesta_ok("Cliente registrado exitosamente", creado)