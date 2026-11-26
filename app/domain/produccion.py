from datetime import date
from enum import Enum
from math import ceil
from pydantic import BaseModel, Field, model_validator

from app.domain.errores import ReglaNegocioError


class EstadoOrden(str, Enum):
    PROGRAMADO = "PROGRAMADO"
    EN_PRODUCCION = "EN_PRODUCCION"


class ResultadoInspeccion(str, Enum):
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


def calcular_unidades_por_dia(cantidad: int, fecha_inicio: date, fecha_fin: date) -> int:
    dias = (fecha_fin - fecha_inicio).days + 1
    return ceil(cantidad / dias)


class LineaProduccion:
    def __init__(self, nombre: str, capacidad_diaria: int):
        self.nombre = nombre
        self.capacidad_diaria = capacidad_diaria

    def validar_capacidad(self, unidades_dia_nuevas: int, unidades_dia_ocupadas: int) -> None:
        # RN-30: no se excede la capacidad diaria de la línea
        if unidades_dia_nuevas + unidades_dia_ocupadas > self.capacidad_diaria:
            raise ReglaNegocioError(
                "No se puede programar la producción: se excede la capacidad diaria de la línea",
                {"linea": self.nombre, "capacidadDiaria": self.capacidad_diaria,
                 "unidadesPorDiaOcupadas": unidades_dia_ocupadas,
                 "unidadesPorDiaSolicitadas": unidades_dia_nuevas},
            )


class OrdenProduccion:
    def __init__(self, id: int, id_pedido: int, linea: str, fecha_inicio: date,
                 fecha_fin: date, cantidad: int,
                 estado: EstadoOrden = EstadoOrden.PROGRAMADO,
                 prendas_terminadas: int = 0):
        self.id = id
        self.id_pedido = id_pedido
        self.linea = linea
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.cantidad = cantidad
        self.estado = estado
        self.prendas_terminadas = prendas_terminadas

    def unidades_por_dia(self) -> int:
        return calcular_unidades_por_dia(self.cantidad, self.fecha_inicio, self.fecha_fin)

    def solapa_con(self, inicio: date, fin: date) -> bool:
        return self.fecha_inicio <= fin and inicio <= self.fecha_fin

    def validar_lote_para_inspeccion(self) -> None:
        # RN-28: solo se inspecciona un lote de prendas terminadas
        if self.prendas_terminadas <= 0:
            raise ReglaNegocioError(
                "No hay un lote de prendas terminadas para inspeccionar",
                {"idOrden": self.id, "prendasTerminadas": self.prendas_terminadas},
            )


class InspeccionCalidad:
    def __init__(self, id: int, id_orden: int, resultado: ResultadoInspeccion,
                 prendas_inspeccionadas: int):
        self.id = id
        self.id_orden = id_orden
        self.resultado = resultado
        self.prendas_inspeccionadas = prendas_inspeccionadas


class OrdenProduccionRequest(BaseModel):
    idPedido: int
    fechaInicio: date
    fechaFin: date
    linea: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fechaFin < self.fechaInicio:
            raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio")
        return self


class OrdenProduccionResponse(BaseModel):
    idOrden: int
    idPedido: int
    linea: str
    fechaInicio: date
    fechaFin: date
    estado: EstadoOrden


class InspeccionRequest(BaseModel):
    idOrden: int
    resultado: ResultadoInspeccion


class InspeccionResponse(BaseModel):
    idInspeccion: int
    idOrden: int
    resultado: ResultadoInspeccion
    prendasInspeccionadas: int