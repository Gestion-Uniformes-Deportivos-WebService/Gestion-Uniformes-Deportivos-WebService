# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — HU-003: autorizar el pase a producción
# Comunicación interna: MOD-03 (pagos), MOD-04 (diseño) y ficha técnica.
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────

import logging

from app.core.excepciones import (
    EntradaInvalidaError,
    ErrorRepositorio,
    ReglaNegocioError,
    ServicioNoDisponibleError,
)
from app.domain.estado_pedido import (
    AutorizacionProduccionResponse,
    EstadoPedido,
    PedidoEstadoUpdate,
)
from app.domain.pago import Pago, ResumenPago
from app.domain.pedido import ESTADO_EN_PRODUCCION, validar_id_pedido
from app.repositories.diseno_repo import DisenoRepository
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.pedido_repository import PedidoRepository
from app.services.pedido_service import PedidoService

logger = logging.getLogger(__name__)

AREA_NOTIFICADA = "Confección"


class AutorizacionProduccionService:

    def __init__(self, pedidos: PedidoRepository, pagos: PagoRepository,
                 fichas: FichaTecnicaRepository, disenos: DisenoRepository,
                 pedido_service: PedidoService):
        self.pedidos = pedidos
        self.pagos = pagos                    # MOD-03: anticipo
        self.fichas = fichas                  # ficha técnica
        self.disenos = disenos                # MOD-04: diseño aprobado
        self.pedido_service = pedido_service  # MOD-01: valor total del pedido

    def autorizar(self, id_texto: str,
                  datos: PedidoEstadoUpdate) -> AutorizacionProduccionResponse:
        # El id del pedido debe ser numérico → 400
        try:
            id_pedido = validar_id_pedido(id_texto)
        except ValueError as e:
            raise EntradaInvalidaError(str(e))

        try:
            # El pedido debe existir
            pedido = self.pedidos.obtener_por_id(id_pedido)
            if pedido is None:
                raise ReglaNegocioError(
                    "El pedido consultado no existe", {"idPedido": id_pedido}
                )
            situacion = {"idPedido": id_pedido, "estado": pedido.estado}

            # Este servicio solo autoriza el pase a producción
            if datos.nuevoEstado != ESTADO_EN_PRODUCCION:
                raise ReglaNegocioError(
                    "Por ahora solo se puede autorizar el pase a producción del pedido.",
                    situacion,
                )

            # RN-06: el estado solo avanza en la secuencia definida
            if not EstadoPedido.puede_avanzar(pedido.estado, ESTADO_EN_PRODUCCION):
                raise ReglaNegocioError(
                    "No se puede autorizar producción: el pedido ya se encuentra "
                    f"en estado {pedido.estado}",
                    situacion,
                )

            # RN-15: anticipo del 50% verificado
            total = self.pedido_service.calcular_total(pedido)
            resumen = ResumenPago(total, self.pagos.total_pagado(pedido.id))
            if not Pago.anticipo_verificado(resumen):
                raise ReglaNegocioError(
                    "No se puede autorizar producción: el anticipo del 50% "
                    "no está verificado",
                    situacion,
                )

            # RN-04: ficha técnica completa (tallas, dorsales y nombres)
            ficha = self.fichas.obtener_por_pedido(pedido.id)
            if ficha is None or not ficha.esta_completa():
                raise ReglaNegocioError(
                    "No se puede autorizar producción: la ficha técnica "
                    "no está completa",
                    situacion,
                )

            # RN-07: el diseño debe estar aprobado
            try:
                nuevo_estado = pedido.autorizar_produccion(
                    self.disenos.tiene_diseno_aprobado(pedido.id)
                )
            except ValueError as e:
                raise ReglaNegocioError(str(e), situacion)

            # Todo en orden: cambiar el estado y notificar a confección
            estado_anterior = pedido.estado
            self.pedidos.actualizar_estado(pedido.id, nuevo_estado)

        except ErrorRepositorio:
            # Falla del almacenamiento → 503
            raise ServicioNoDisponibleError(
                "No fue posible autorizar el pase a producción"
            )

        logger.info("Pedido %s autorizado para producción; área notificada: %s",
                    pedido.id, AREA_NOTIFICADA)
        return AutorizacionProduccionResponse(
            idPedido=pedido.id,
            estadoAnterior=estado_anterior,
            estadoNuevo=nuevo_estado,
            areaNotificada=AREA_NOTIFICADA,
        )
    