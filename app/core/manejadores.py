# ─────────────────────────────────────────────────────────────
# CORE — manejadores globales de errores
# Convierten cualquier error al formato {mensaje, data, success}
# usando los códigos HTTP documentados en cada HU.
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.excepciones import ErrorAplicacion
from app.core.respuesta import respuesta_error


def _mensaje_validacion(error: dict) -> str:
    """Traduce el primer error de Pydantic a un mensaje claro."""
    loc = [str(p) for p in error.get("loc", ()) if p != "body"]
    campo = loc[-1] if loc else None
    tipo = error.get("type", "")

    if tipo == "json_invalid" or campo is None:
        return "El cuerpo de la solicitud no es un JSON válido"
    if tipo == "missing":
        return f"El campo {campo} es obligatorio"
    if tipo == "value_error":
        # Mensajes propios de los validadores del dominio
        return str(error.get("msg", "")).removeprefix("Value error, ")
    return f"El campo {campo} no es válido: {error.get('msg', '')}"


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorAplicacion)
    async def _error_aplicacion(_: Request, exc: ErrorAplicacion):
        return JSONResponse(
            status_code=exc.codigo_http,
            content=respuesta_error(exc.mensaje, exc.data),
        )

    @app.exception_handler(RequestValidationError)
    async def _error_validacion(_: Request, exc: RequestValidationError):
        errores = exc.errors()
        mensaje = _mensaje_validacion(errores[0]) if errores else "Solicitud inválida"
        return JSONResponse(status_code=400, content=respuesta_error(mensaje, {}))

    @app.exception_handler(Exception)
    async def _error_inesperado(_: Request, __: Exception):
        return JSONResponse(
            status_code=500,
            content=respuesta_error("Error interno del servidor", {}),
        )
