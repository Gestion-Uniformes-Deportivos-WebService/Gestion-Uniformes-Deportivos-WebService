from app.domain.diseno import DisenoAprobacionResponse
from app.domain.errores import RecursoNoEncontradoError, ReglaNegocioError
from app.repositories.diseno_repo import DisenoRepository


class DisenoService:

    def __init__(self, repo: DisenoRepository):
        self.repo = repo

    def enviar_a_aprobacion(self, id_diseno: int) -> DisenoAprobacionResponse:
        diseno = self.repo.obtener_por_id(id_diseno)
        if not diseno:
            raise RecursoNoEncontradoError(
                "El diseño indicado no existe", {"idDiseno": id_diseno}
            )

        # RN-25: un pedido no puede tener dos diseños pendientes a la vez
        pendiente = self.repo.obtener_pendiente_por_pedido(diseno.id_pedido)
        if pendiente and pendiente.id != diseno.id:
            raise ReglaNegocioError(
                "El pedido ya tiene un diseño pendiente de aprobación",
                {"idPedido": diseno.id_pedido, "idDisenoPendiente": pendiente.id},
            )

        diseno.enviar_a_aprobacion()   # reglas del Domain
        self.repo.guardar(diseno)

        # La notificación al cliente se simula; la integración real queda fuera del alcance
        return DisenoAprobacionResponse(
            idDiseno=diseno.id,
            idPedido=diseno.id_pedido,
            estado=diseno.estado,
            clienteNotificado=True,
        )