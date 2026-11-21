# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — orquesta dominio + repositorios
# Comunicación interna: MOD-03 → MOD-01 (consulta del total del pedido).
# No importa nada de FastAPI.
# ─────────────────────────────────────────────────────────────

from app.core.excepciones import (
    ErrorRepositorio,
    ReglaNegocioError,
    ServicioNoDisponibleError,
)
from app.domain.pago import (
    ESTADO_PAGO_ABONADO,
    ESTADO_PAGO_PARCIAL,
    TIPO_ANTICIPO,
    Pago,
    PagoAnticipoCreate,
    PagoResponse,
    ResumenPago,
)
from app.repositories.pago_repository import PagoRepository
from app.repositories.pedido_repository import PedidoRepository
from app.services.pedido_service import PedidoService


class PagoService:

    def __init__(self, repo: PagoRepository, pedidos: PedidoRepository,
                 pedido_service: PedidoService):
        self.repo = repo
        self.pedidos = pedidos                # MOD-01: pedidos
        self.pedido_service = pedido_service  # MOD-01: valor total del pedido

    def registrar_anticipo(self, datos: PagoAnticipoCreate) -> tuple[PagoResponse, str]:
        """Registra un abono al anticipo. Devuelve (data, mensaje)."""
        try:
            # El pedido debe existir
            pedido = self.pedidos.obtener_por_id(datos.idPedido)
            if pedido is None:
                raise ReglaNegocioError(
                    "El pedido consultado no existe",
                    {"idPedido": datos.idPedido},
                    codigo_http=422,
                )

            # RN-20: el pedido debe estar activo
            try:
                Pago.pedido_activo(pedido.estado)
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e),
                    {"idPedido": datos.idPedido, "estado": pedido.estado},
                    codigo_http=422,
                )

            # El comprobante no puede haberse usado antes
            if self.repo.existe_comprobante(datos.comprobante):
                raise ReglaNegocioError(
                    "El comprobante ya fue registrado",
                    {"comprobante": datos.comprobante},
                    codigo_http=422,
                )

            # Cuánto vale el pedido y cuánto se ha pagado (RN-14: anticipo = 50%)
            total = self.pedido_service.calcular_total(pedido)
            resumen_antes = ResumenPago(total, self.repo.total_pagado(pedido.id))

            # RN-17: el abono no puede superar el valor pendiente
            candidato = Pago(0, pedido.id, datos.monto, TIPO_ANTICIPO,
                             datos.comprobante, "")
            try:
                candidato.validar_monto(resumen_antes.pendiente)
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e),
                    {"montoRecibido": datos.monto,
                     "valorPendiente": resumen_antes.pendiente},
                    codigo_http=422,
                )

            # ¿Con este abono el acumulado alcanza el 50%?
            resumen_despues = ResumenPago(total, resumen_antes.pagado + datos.monto)
            estado_pago = (ESTADO_PAGO_ABONADO if resumen_despues.anticipo_completo()
                           else ESTADO_PAGO_PARCIAL)

            creado = self.repo.crear(pedido.id, datos.monto, TIPO_ANTICIPO,
                                     datos.comprobante, estado_pago)

        except ErrorRepositorio:
            # Falla del almacenamiento → 503
            raise ServicioNoDisponibleError("No fue posible registrar el anticipo")

        mensaje = f"Anticipo registrado exitosamente. {resumen_despues.mensaje_abono()}"
        return PagoResponse(**creado.to_response()), mensaje