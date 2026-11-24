from app.domain.despacho import (
    DespachoRequest, DespachoResponse, FaltanteItem, VerificacionResponse,
)
from app.domain.errores import RecursoNoEncontradoError, ReglaNegocioError
from app.repositories.despacho_repo import DespachoRepository
from app.repositories.pedido_despacho_stub_repo import PedidoDespachoStubRepository


class DespachoService:

    def __init__(self, repo: DespachoRepository, pedido_repo: PedidoDespachoStubRepository):
        self.repo = repo
        self.pedido_repo = pedido_repo

    # ---------------- HU-030
    def verificar_pedido(self, id_pedido: int) -> VerificacionResponse:
        empaque = self.repo.obtener_por_pedido(id_pedido)
        if not empaque:
            raise RecursoNoEncontradoError(
                "El pedido consultado no existe", {"idPedido": id_pedido}
            )

        empaque.validar_sin_no_conformidades()   # RN-29

        if empaque.esta_completo():              # RN-39
            empaque.marcar_listo_para_despacho()
            self.repo.guardar(empaque)
            return VerificacionResponse(
                idPedido=id_pedido, prendasOrden=empaque.prendas_orden(),
                prendasEmpacadas=empaque.prendas_empacadas(),
                completo=True, estado=empaque.estado,
            )

        # RN-42: con faltantes el pedido no pasa a despacho
        return VerificacionResponse(
            idPedido=id_pedido, prendasOrden=empaque.prendas_orden(),
            prendasEmpacadas=empaque.prendas_empacadas(), completo=False,
            faltantes=[FaltanteItem(**f) for f in empaque.faltantes()],
        )

    # ---------------- HU-029
    def generar_guia(self, datos: DespachoRequest) -> DespachoResponse:
        pedido = self.pedido_repo.obtener_por_id(datos.idPedido)
        if not pedido:
            raise RecursoNoEncontradoError(
                "El pedido indicado no existe", {"idPedido": datos.idPedido}
            )
        transportadora = self.repo.obtener_transportadora(datos.transportadora)
        if not transportadora:
            raise RecursoNoEncontradoError(
                "La transportadora indicada no existe", {"transportadora": datos.transportadora}
            )

        # RN-43: una sola guía por pedido
        existente = self.repo.obtener_despacho_por_pedido(pedido.id)
        if existente:
            raise ReglaNegocioError(
                "El pedido ya tiene una guía de despacho",
                {"idPedido": pedido.id, "guia": existente.guia},
            )

        pedido.validar_paz_y_salvo()             # RN-38 y RN-16

        empaque = self.repo.obtener_por_pedido(pedido.id)
        if not empaque:
            raise RecursoNoEncontradoError(
                "El pedido no tiene empaque registrado", {"idPedido": pedido.id}
            )
        empaque.validar_sin_no_conformidades()   # RN-29
        empaque.validar_completo()               # RN-42

        transportadora.validar_para_zona(pedido.zona_destino)   # RN-40

        despacho = self.repo.crear_despacho(pedido.id, transportadora.nombre)
        return DespachoResponse(
            idDespacho=despacho.id, idPedido=despacho.id_pedido,
            transportadora=despacho.transportadora, guia=despacho.guia,
            estado=despacho.estado,
        )