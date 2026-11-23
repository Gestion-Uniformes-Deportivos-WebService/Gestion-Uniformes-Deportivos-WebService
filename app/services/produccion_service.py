from app.domain.errores import (
    RecursoNoEncontradoError, ReglaNegocioError, ValidacionDominioError,
)
from app.domain.produccion import (
    OrdenProduccionRequest, OrdenProduccionResponse, calcular_unidades_por_dia,
)
from app.repositories.diseno_repo import DisenoRepository
from app.repositories.inventario_repo import InventarioRepository
from app.repositories.pedido_stub_repo import PedidoStubRepository
from app.repositories.produccion_repo import ProduccionRepository


class ProduccionService:

    def __init__(self, repo: ProduccionRepository, pedido_repo: PedidoStubRepository,
                 diseno_repo: DisenoRepository, inventario_repo: InventarioRepository):
        self.repo = repo
        self.pedido_repo = pedido_repo
        self.diseno_repo = diseno_repo
        self.inventario_repo = inventario_repo

    def programar_orden(self, datos: OrdenProduccionRequest) -> OrdenProduccionResponse:
        pedido = self.pedido_repo.obtener_por_id(datos.idPedido)
        if not pedido:
            raise RecursoNoEncontradoError(
                "El pedido indicado no existe", {"idPedido": datos.idPedido}
            )
        linea = self.repo.obtener_linea(datos.linea)
        if not linea:
            raise RecursoNoEncontradoError(
                "La línea de producción indicada no existe", {"linea": datos.linea}
            )
        existente = self.repo.obtener_por_pedido(pedido.id)
        if existente:
            raise ReglaNegocioError(
                "El pedido ya tiene una orden de producción",
                {"idPedido": pedido.id, "idOrden": existente.id},
            )

        # RN-21: el diseño debe estar aprobado
        if not self.diseno_repo.tiene_diseno_aprobado(pedido.id):
            raise ReglaNegocioError(
                "No se puede programar la producción: el diseño del pedido no está aprobado",
                {"idPedido": pedido.id},
            )
        # RN-27: la ficha técnica debe estar completa
        if not pedido.ficha_completa:
            raise ValidacionDominioError(
                "No se puede programar la producción: la ficha técnica del pedido no está completa",
                {"idPedido": pedido.id},
            )
        # RN-26: debe haber stock suficiente de insumos
        faltantes = []
        for nombre, requerido in pedido.insumos_requeridos.items():
            insumo = self.inventario_repo.obtener_insumo(nombre)
            disponible = insumo.stock if insumo else 0
            if disponible < requerido:
                faltantes.append(
                    {"insumo": nombre, "requerido": requerido, "disponible": disponible}
                )
        if faltantes:
            raise ReglaNegocioError(
                "No se puede programar la producción: stock insuficiente de insumos",
                {"insumosFaltantes": faltantes},
            )
        # RN-30: no se excede la capacidad diaria de la línea
        nuevas = calcular_unidades_por_dia(pedido.cantidad, datos.fechaInicio, datos.fechaFin)
        ocupadas = sum(
            o.unidades_por_dia()
            for o in self.repo.ordenes_de_linea_solapadas(
                linea.nombre, datos.fechaInicio, datos.fechaFin)
        )
        linea.validar_capacidad(nuevas, ocupadas)

        orden = self.repo.crear(pedido.id, linea.nombre, datos.fechaInicio,
                                datos.fechaFin, pedido.cantidad)
        # La notificación al área de confección se simula
        return OrdenProduccionResponse(
            idOrden=orden.id, idPedido=orden.id_pedido, linea=orden.linea,
            fechaInicio=orden.fecha_inicio, fechaFin=orden.fecha_fin, estado=orden.estado,
        )