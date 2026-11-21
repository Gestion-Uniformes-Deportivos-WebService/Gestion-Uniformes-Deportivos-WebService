# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — orquesta dominio + repositorios
# Comunicación interna: MOD-01 → MOD-02 (clientes) y MOD-08 (parámetros).
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────


from app.core.excepciones import (
    EntradaInvalidaError,
    ErrorRepositorio,
    RecursoNoEncontradoError,
    ReglaNegocioError,
    ServicioNoDisponibleError,
)
from app.domain.pedido import (
    CANTIDAD_MINIMA_DEFAULT,
    COSTO_UNITARIO_DEFAULT,
    ESTADO_PENDIENTE_ANTICIPO,
    CotizacionResponse,
    EsquemaDePago,
    Pedido,
    PedidoCreate,
    PedidoResponse,
    validar_id_pedido,
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

    def _costo_unitario(self) -> int:
        """Lee COSTO_UNITARIO_PRENDA de MOD-01; si no existe, usa 45.000."""
        p = self.parametros.obtener_por_modulo_y_nombre("MOD-01", "COSTO_UNITARIO_PRENDA")
        if p is not None and p.tipo == "entero" and int(p.valor) > 0:
            return int(p.valor)
        return COSTO_UNITARIO_DEFAULT

    def cotizar(self, id_texto: str) -> CotizacionResponse:
        # Paso 1: validar que el id sea numérico → 400
        try:
            id_pedido = validar_id_pedido(id_texto)
        except ValueError as e:
            raise EntradaInvalidaError(str(e))

        # Paso 2: consultar el pedido y la tarifa; si falla el almacenamiento → 503
        try:
            pedido = self.repo.obtener_por_id(id_pedido)
            if pedido is None:
                raise RecursoNoEncontradoError(
                    "El pedido consultado no existe", {"idPedido": id_pedido}
                )
            costo_unitario = self._costo_unitario()
        except ErrorRepositorio:
            raise ServicioNoDisponibleError("No fue posible calcular la cotización")

        # Paso 3: costo total y desglose 50/50 (RN-14, RN-50)
        costo_total = pedido.calcular_costo_total(costo_unitario)
        try:
            anticipo, saldo = pedido.esquema_pago.recalcular(costo_total)
        except ValueError as e:
            raise ReglaNegocioError(str(e), {"idPedido": id_pedido}, codigo_http=404)

        # Paso 4: retornar el desglose
        return CotizacionResponse(
            idPedido=pedido.id,
            cantidad=pedido.cantidad,
            costoUnitario=costo_unitario,
            costoTotal=costo_total,
            anticipo=anticipo,
            saldoFinal=saldo,
        )