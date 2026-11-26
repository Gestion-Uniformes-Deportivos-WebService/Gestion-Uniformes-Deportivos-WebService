# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — orquesta dominio + repositorio
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────

from app.core.excepciones import (
    ErrorRepositorio,
    ReglaNegocioError,
    ServicioNoDisponibleError,
)
from app.domain.cliente import Cliente, ClienteCreate, ClienteResponse, DireccionEnvio
from app.repositories.cliente_repository import ClienteRepository


class ClienteService:

    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def registrar(self, datos: ClienteCreate) -> ClienteResponse:
        # RN-09 ya se validó en el dominio (ClienteCreate.nit)
        try:
            # RN-10: no puede haber dos cuentas activas con el mismo NIT
            if self.repo.obtener_activo_por_nit(datos.nit):
                raise ReglaNegocioError(
                    "Ya existe un cliente activo con el NIT indicado",
                    {"nit": datos.nit},
                )

            # RN-12: la dirección recibida se registra como la primera dirección de envío
            direcciones = [DireccionEnvio(datos.direccion, principal=True)]
            candidato = Cliente(0, datos.nit, datos.nombre, datos.email, direcciones)
            try:
                candidato.validar_direccion_envio()
            except ValueError as e:
                raise ReglaNegocioError(str(e), {"nit": datos.nit})

            creado = self.repo.crear(datos.nit, datos.nombre, datos.email, direcciones)

        except ErrorRepositorio:
            # Falla del almacenamiento → 503
            raise ServicioNoDisponibleError("No fue posible registrar el cliente")

        return ClienteResponse(**creado.to_response())