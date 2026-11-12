from typing import Optional


class ErrorDominio(Exception):
    """Base de los errores de negocio. No conoce HTTP."""

    def __init__(self, mensaje: str, data: Optional[dict] = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.data = data or {}


class RecursoNoEncontradoError(ErrorDominio):
    """El recurso pedido no existe."""


class ReglaNegocioError(ErrorDominio):
    """Se viola una regla de negocio (conflicto de estado)."""


class ValidacionDominioError(ErrorDominio):
    """Los datos no cumplen una validación del dominio."""