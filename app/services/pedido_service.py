# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — orquesta dominio + repositorios
# Comunicación interna: MOD-01 → MOD-02 (clientes) y MOD-08 (parámetros).
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────

from app.core.excepciones import (
    ErrorRepositorio,
    ReglaNegocioError,
    ServicioNoDisponibleError,
)
from app.domain.pedido import (
    CANTIDAD_MINIMA_DEFAULT,
    ESTADO_PENDIENTE_ANTICIPO,
    EsquemaDePago,
    Pedido,
    PedidoCreate,
    PedidoResponse,
)
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.parametro_repository import ParametroRepository
from app.repositories.pedido_repository import PedidoRepository


class PedidoService:

    def __init__(self, repo: PedidoRepository,
                 clientes: ClienteRepository,
                 parametros: ParametroRepository):
        self.repo = repo
        self.clientes = clientes      # MOD-02: validación de cliente
        self.parametros = parametros  # MOD-08: parámetros del pedido

    def _cantidad_minima(self) -> int:
        """Lee CANTIDAD_MINIMA_PEDIDO de MOD-01; si no existe, usa 6 (RN-01)."""
        p = self.parametros.obtener_por_modulo_y_nombre("MOD-01", "CANTIDAD_MINIMA_PEDIDO")
        if p is not None and p.tipo == "entero" and int(p.valor) > 0:
            return int(p.valor)
        return CANTIDAD_MINIMA_DEFAULT

    def registrar(self, datos: PedidoCreate) -> PedidoResponse:
        try:
            # RN-02 y RN-12: cliente existente, activo y con dirección de envío
            cliente = self.clientes.obtener_por_id(datos.idCliente)
            try:
                Pedido.validar_cliente_activo(cliente)   # RN-02
                cliente.validar_direccion_envio()        # RN-12
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e), {"idCliente": datos.idCliente}, codigo_http=422
                )

            # RN-01: cantidad mínima (parámetro del sistema)
            minimo = self._cantidad_minima()
            esquema = EsquemaDePago()
            prendas = [p.model_dump() for p in datos.listaPrendas]
            candidato = Pedido(0, datos.idCliente, prendas, datos.cantidad,
                               ESTADO_PENDIENTE_ANTICIPO, esquema)
            try:
                candidato.validar_cantidad_minima(minimo)
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e),
                    {"cantidad": datos.cantidad, "cantidadMinima": minimo},
                    codigo_http=422,
                )

            # RN-14: esquema de pago 50/50
            try:
                esquema.validar()
            except ValueError as e:
                raise ReglaNegocioError(str(e), {"esquemaPago": str(esquema)},
                                        codigo_http=422)

            # Guardar el pedido en estado PENDIENTE_ANTICIPO
            creado = self.repo.crear(datos.idCliente, prendas, datos.cantidad,
                                     ESTADO_PENDIENTE_ANTICIPO, esquema)

        except ErrorRepositorio:
            # Falla del almacenamiento → 503
            raise ServicioNoDisponibleError("No fue posible registrar el pedido")

        return PedidoResponse(**creado.to_response())