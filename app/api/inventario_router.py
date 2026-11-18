from fastapi import APIRouter, status

from app.core.responses import RespuestaApi
from app.domain.inventario import MovimientoRequest, MovimientoResponse
from app.repositories.inventario_repo import inventario_repository
from app.services.inventario_service import InventarioService

router = APIRouter(prefix="/api/inventario", tags=["Inventario"])
service = InventarioService(repo=inventario_repository)


@router.post(
    "/movimientos",
    response_model=RespuestaApi[MovimientoResponse],
    status_code=status.HTTP_201_CREATED,
)
def registrar_movimiento_de_inventario(datos: MovimientoRequest):
    """HU-025: registra una entrada o salida de insumo."""
    resultado = service.registrar_movimiento(datos)
    return {"mensaje": "Movimiento registrado exitosamente", "data": resultado, "success": True}