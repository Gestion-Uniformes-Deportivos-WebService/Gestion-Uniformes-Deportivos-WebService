from typing import Generic, TypeVar
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.domain.errores import (
    ErrorDominio, RecursoNoEncontradoError,
    ReglaNegocioError, ValidacionDominioError,
)

T = TypeVar("T")


class RespuestaApi(BaseModel, Generic[T]):
    mensaje: str
    data: T
    success: bool = True


def _error(codigo: int, mensaje: str, data: dict) -> JSONResponse:
    return JSONResponse(
        status_code=codigo,
        content={"mensaje": mensaje, "data": data, "success": False},
    )


async def manejar_error_dominio(request: Request, exc: ErrorDominio):
    if isinstance(exc, RecursoNoEncontradoError):
        codigo = 404
    elif isinstance(exc, ReglaNegocioError):
        codigo = 409
    elif isinstance(exc, ValidacionDominioError):
        codigo = 422
    else:
        codigo = 400
    return _error(codigo, exc.mensaje, exc.data)


async def manejar_validacion(request: Request, exc: RequestValidationError):
    errores = [
        {"campo": ".".join(str(p) for p in e["loc"]), "detalle": e["msg"]}
        for e in exc.errors()
    ]
    return _error(400, "Datos de entrada no válidos", {"errores": errores})