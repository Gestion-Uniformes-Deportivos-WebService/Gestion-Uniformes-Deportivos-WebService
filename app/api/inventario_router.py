from typing import List
from fastapi import APIRouter, Query, status

from app.core.responses import RespuestaApi
from app.domain.inventario import (
    DisponibilidadResponse, MovimientoRequest, MovimientoResponse,
)
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


@router.get(
    "/disponibilidad",
    response_model=RespuestaApi[DisponibilidadResponse],
    response_model_exclude_none=True,
)
def consultar_disponibilidad_de_insumos(insumos: List[str] = Query(..., alias="insumos[]")):
    """HU-026: verifica si hay stock de los insumos indicados."""
    resultado = service.consultar_disponibilidad(insumos)
    if resultado.disponible:
        return {"mensaje": "Hay disponibilidad de todos los insumos consultados",
                "data": resultado, "success": True}
    return {"mensaje": "Existen insumos con faltante de stock",
            "data": resultado, "success": False}