from app.domain.errores import RecursoNoEncontradoError
from app.domain.inventario import (
    DisponibilidadResponse, InsumoStock,
    MovimientoRequest, MovimientoResponse, TipoMovimiento,
)
from app.repositories.inventario_repo import InventarioRepository


class InventarioService:

    def __init__(self, repo: InventarioRepository):
        self.repo = repo

    def registrar_movimiento(self, datos: MovimientoRequest) -> MovimientoResponse:
        insumo = self.repo.obtener_insumo(datos.insumo)
        if not insumo:
            raise RecursoNoEncontradoError(
                "El insumo indicado no existe", {"insumo": datos.insumo}
            )

        if datos.tipo == TipoMovimiento.ENTRADA:
            insumo.registrar_entrada(datos.cantidad)
        else:
            insumo.registrar_salida(datos.cantidad)   # reglas del Domain

        mov = self.repo.registrar_movimiento(insumo, datos.tipo, datos.cantidad)
        return MovimientoResponse(
            idMovimiento=mov.id, insumo=mov.insumo, tipo=mov.tipo,
            cantidad=mov.cantidad, saldoDisponible=mov.saldo_disponible,
        )

    def consultar_disponibilidad(self, nombres: list[str]) -> DisponibilidadResponse:
        detalle = []
        for nombre in nombres:
            insumo = self.repo.obtener_insumo(nombre)
            if not insumo:
                raise RecursoNoEncontradoError(
                    "El insumo indicado no existe", {"insumo": nombre}
                )
            detalle.append(insumo)

        faltantes = [InsumoStock(insumo=i.nombre, stock=i.stock)
                     for i in detalle if not i.tiene_stock()]
        if faltantes:
            return DisponibilidadResponse(disponible=False, faltantes=faltantes)
        return DisponibilidadResponse(
            disponible=True,
            insumos=[InsumoStock(insumo=i.nombre, stock=i.stock) for i in detalle],
        )