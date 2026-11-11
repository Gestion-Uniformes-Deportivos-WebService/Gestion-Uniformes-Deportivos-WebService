# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — orquesta dominio + repositorio
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────

from app.core.excepciones import (
    ErrorRepositorio,
    ReglaNegocioError,
    ServicioNoDisponibleError,
)
from app.domain.parametro import Parametro, ParametroCreate, ParametroResponse
from app.repositories.parametro_repository import ParametroRepository


class ParametroService:

    def __init__(self, repo: ParametroRepository):
        self.repo = repo

    def registrar(self, datos: ParametroCreate) -> ParametroResponse:
        try:
            # RN-46: no puede existir el mismo parámetro para el módulo
            if self.repo.obtener_por_modulo_y_nombre(datos.modulo, datos.nombre):
                raise ReglaNegocioError(
                    "Ya existe un parámetro con ese nombre para el módulo indicado",
                    {"modulo": datos.modulo, "nombre": datos.nombre},
                )

            # RN-47: el valor debe cumplir el tipo y rango definidos
            candidato = Parametro(0, datos.modulo, datos.nombre, datos.valor)
            try:
                candidato.validar_valor()
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e), {"modulo": datos.modulo, "nombre": datos.nombre}
                )

            creado = self.repo.crear(
                datos.modulo, datos.nombre, datos.valor,
                tipo=candidato.tipo, rango=candidato.rango,
            )
        except ErrorRepositorio:
            raise ServicioNoDisponibleError("No fue posible registrar el parámetro")

        return ParametroResponse(**creado.to_response())
