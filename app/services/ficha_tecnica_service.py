# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — orquesta dominio + repositorios
# Consulta el pedido (MOD-01) para validar la ficha contra sus unidades.
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────

from app.core.excepciones import (
    EntradaInvalidaError,
    ErrorRepositorio,
    ReglaNegocioError,
    ServicioNoDisponibleError,
)
from app.domain.ficha_tecnica import (
    FichaTecnica,
    FichaTecnicaCreate,
    FichaTecnicaResponse,
)
from app.domain.pedido import validar_id_pedido
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.repositories.pedido_repository import PedidoRepository


class FichaTecnicaService:

    def __init__(self, repo: FichaTecnicaRepository, pedidos: PedidoRepository):
        self.repo = repo
        self.pedidos = pedidos

    def registrar(self, id_texto: str, datos: FichaTecnicaCreate) -> FichaTecnicaResponse:
        # Paso 1: el id del pedido debe ser numérico → 400
        try:
            id_pedido = validar_id_pedido(id_texto)
        except ValueError as e:
            raise EntradaInvalidaError(str(e))

        try:
            # El pedido debe existir
            pedido = self.pedidos.obtener_por_id(id_pedido)
            if pedido is None:
                raise ReglaNegocioError(
                    "El pedido consultado no existe",
                    {"idPedido": id_pedido},
                    codigo_http=422,
                )

            # RN-03: no se puede modificar un pedido que ya está en producción
            try:
                pedido.validar_modificable()
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e),
                    {"idPedido": id_pedido, "estado": pedido.estado},
                    codigo_http=422,
                )

            candidata = FichaTecnica(0, id_pedido, datos.tallas,
                                     datos.dorsales, datos.nombres)

            # Paso 2 — RN-08: tallas/dorsales/nombres coinciden con las unidades
            try:
                candidata.validar_consistencia(pedido.cantidad)
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e),
                    {"unidadesPedido": pedido.cantidad,
                     "unidadesRecibidas": candidata.unidades_recibidas()},
                    codigo_http=422,
                )

            # RN-04: la ficha debe estar completa
            if not candidata.esta_completa():
                raise ReglaNegocioError(
                    "La ficha técnica debe incluir tallas, dorsales y nombres completos",
                    {"idPedido": id_pedido},
                    codigo_http=422,
                )

            # Pasos 3 y 4: asociar y guardar la ficha técnica
            creada = self.repo.guardar(id_pedido, datos.tallas,
                                       datos.dorsales, datos.nombres)

        except ErrorRepositorio:
            # Falla del almacenamiento → 503
            raise ServicioNoDisponibleError("No fue posible registrar la ficha técnica")

        return FichaTecnicaResponse(**creada.to_response())