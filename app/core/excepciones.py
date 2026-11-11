# ─────────────────────────────────────────────────────────────
# CORE — excepciones compartidas por todas las capas
# Cada excepción lleva su código HTTP y los datos que se
# devuelven en el campo "data" del JSON estandarizado.
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────


class ErrorAplicacion(Exception):
    """Base: error controlado que la API convierte en {mensaje, data, success}."""

    codigo_http: int = 500

    def __init__(self, mensaje: str, data: dict | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.data = data if data is not None else {}


class EntradaInvalidaError(ErrorAplicacion):
    codigo_http = 400


class RecursoNoEncontradoError(ErrorAplicacion):
    codigo_http = 404


class ReglaNegocioError(ErrorAplicacion):
    """Regla de negocio incumplida (RN-xx) o consulta sin datos."""

    codigo_http = 409


class ServicioNoDisponibleError(ErrorAplicacion):
    """Falla de base de datos / almacenamiento."""

    codigo_http = 503


class ErrorRepositorio(Exception):
    """Lo lanza el repositorio cuando el almacenamiento falla."""
