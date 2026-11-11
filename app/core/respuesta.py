# ─────────────────────────────────────────────────────────────
# CORE — estructura estándar de respuesta: {mensaje, data, success}
# ─────────────────────────────────────────────────────────────

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class RespuestaApi(BaseModel, Generic[T]):
    mensaje: str
    data: T
    success: bool


def respuesta_ok(mensaje: str, data: Any) -> dict:
    return {"mensaje": mensaje, "data": data, "success": True}


def respuesta_error(mensaje: str, data: Any | None = None) -> dict:
    return {"mensaje": mensaje, "data": data if data is not None else {}, "success": False}
