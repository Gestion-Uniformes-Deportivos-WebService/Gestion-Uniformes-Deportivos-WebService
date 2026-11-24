from app.domain.despacho import FaltanteItem, VerificacionResponse
from app.domain.errores import RecursoNoEncontradoError
from app.repositories.despacho_repo import DespachoRepository


class DespachoService:

    def __init__(self, repo: DespachoRepository):
        self.repo = repo

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