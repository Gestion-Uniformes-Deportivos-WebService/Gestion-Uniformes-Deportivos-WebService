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
    ESTADO_PEDIDO_PAGADO_TOTAL,
    TIPO_ANTICIPO,
    TIPO_SALDO_FINAL,
    Pago,
    PagoAnticipoCreate,
    PagoResponse,
    PagoSaldoCreate,
    PagoSaldoResponse,
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

    def registrar_saldo(self, datos: PagoSaldoCreate) -> PagoSaldoResponse:
        """Registra el pago del saldo final: debe completar el 100% del pedido."""
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

            # Cuánto vale el pedido y cuánto se ha pagado hasta ahora
            total = self.pedido_service.calcular_total(pedido)
            resumen_antes = ResumenPago(total, self.repo.total_pagado(pedido.id))
            pendiente = resumen_antes.pendiente

            # Si ya no hay nada pendiente, no se acepta otro pago
            if pendiente == 0:
                raise ReglaNegocioError(
                    "El pedido ya está pagado en su totalidad",
                    {"idPedido": pedido.id, "saldoPendiente": 0},
                    codigo_http=422,
                )

            # RN-17: el pago no puede superar el valor pendiente
            candidato = Pago(0, pedido.id, datos.monto, TIPO_SALDO_FINAL, "", "")
            try:
                candidato.validar_monto(pendiente)
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e),
                    {"montoRecibido": datos.monto, "saldoPendiente": pendiente},
                    codigo_http=422,
                )

            # El saldo debe completar el 100% del valor del pedido
            if datos.monto < pendiente:
                raise ReglaNegocioError(
                    "El monto no completa el 100% del valor del pedido",
                    {"montoRecibido": datos.monto, "saldoPendiente": pendiente},
                    codigo_http=422,
                )

            creado = self.repo.crear(pedido.id, datos.monto, TIPO_SALDO_FINAL,
                                     "", ESTADO_PAGO_ABONADO)

        except ErrorRepositorio:
            # Falla del almacenamiento → 503
            raise ServicioNoDisponibleError("No fue posible registrar el saldo final")

        resumen_despues = ResumenPago(total, resumen_antes.pagado + datos.monto)
        return PagoSaldoResponse(
            idPago=creado.id,
            idPedido=pedido.id,
            monto=creado.monto,
            tipo=creado.tipo,
            estadoPedido=ESTADO_PEDIDO_PAGADO_TOTAL,
            saldoPendiente=resumen_despues.pendiente,
        )    
    def registrar_saldo(self, datos: PagoSaldoCreate) -> tuple[PagoSaldoResponse, str]:
        """Registra un pago del saldo (total o parcial). Devuelve (data, mensaje)."""
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

            # Cuánto vale el pedido y cuánto se ha pagado hasta ahora
            total = self.pedido_service.calcular_total(pedido)
            resumen_antes = ResumenPago(total, self.repo.total_pagado(pedido.id))
            pendiente = resumen_antes.pendiente

            # Si ya no hay nada pendiente, no se acepta otro pago
            if pendiente == 0:
                raise ReglaNegocioError(
                    "El pedido ya está pagado en su totalidad",
                    {"idPedido": pedido.id, "saldoPendiente": 0},
                    codigo_http=422,
                )

            # RN-17: el pago no puede superar el valor pendiente
            candidato = Pago(0, pedido.id, datos.monto, TIPO_SALDO_FINAL, "", "")
            try:
                candidato.validar_monto(pendiente)
            except ValueError as e:
                raise ReglaNegocioError(
                    str(e),
                    {"montoRecibido": datos.monto, "saldoPendiente": pendiente},
                    codigo_http=422,
                )

            # ¿Con este pago el pedido queda pagado al 100%?
            resumen_despues = ResumenPago(total, resumen_antes.pagado + datos.monto)
            completo = resumen_despues.pendiente == 0
            estado_pago = ESTADO_PAGO_ABONADO if completo else ESTADO_PAGO_PARCIAL

            creado = self.repo.crear(pedido.id, datos.monto, TIPO_SALDO_FINAL,
                                     "", estado_pago)

        except ErrorRepositorio:
            # Falla del almacenamiento → 503
            raise ServicioNoDisponibleError("No fue posible registrar el saldo final")

        respuesta = PagoSaldoResponse(
            idPago=creado.id,
            idPedido=pedido.id,
            monto=creado.monto,
            tipo=creado.tipo,
            estadoPedido=(ESTADO_PEDIDO_PAGADO_TOTAL if completo
                          else ESTADO_PAGO_PARCIAL),
            saldoPendiente=resumen_despues.pendiente,
        )
        titulo = ("Saldo final registrado exitosamente" if completo
                  else "Abono al saldo registrado exitosamente")
        return respuesta, f"{titulo}. {resumen_despues.mensaje_abono()}"