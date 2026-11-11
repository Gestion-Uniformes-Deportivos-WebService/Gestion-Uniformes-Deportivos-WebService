# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — Parametro (MOD-08 / SUB-15)
# RN-46: no se permite un parámetro duplicado (mismo nombre) por módulo.
# RN-47: el valor debe cumplir el tipo de dato y rango definidos al crearse.
# No importa nada de FastAPI ni de almacenamiento.
# ─────────────────────────────────────────────────────────────

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

PATRON_MODULO = re.compile(r"^MOD-\d{2}$")

TIPOS_VALIDOS = ("texto", "entero", "decimal")


# ── Schema de ENTRADA (body del POST) ─────────────────────────
class ParametroCreate(BaseModel):
    modulo: str = Field(..., description="Código del módulo (MOD-NN)")
    nombre: str = Field(..., description="Nombre del parámetro")
    valor: str = Field(..., description="Valor inicial")

    @field_validator("modulo")
    @classmethod
    def modulo_formato(cls, v: str) -> str:
        v = v.strip().upper()
        if not PATRON_MODULO.match(v):
            raise ValueError("El campo modulo debe tener el formato MOD-NN")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("El campo nombre no puede estar vacío")
        if len(v) > 100:
            raise ValueError("El campo nombre no puede superar 100 caracteres")
        return v

    @field_validator("valor")
    @classmethod
    def valor_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El campo valor no puede estar vacío")
        return v


# ── Schema de SALIDA (data del JSON) ──────────────────────────
class ParametroResponse(BaseModel):
    idParametro: int
    modulo: str
    nombre: str
    valor: str


# ── Entidad del dominio ───────────────────────────────────────
class Parametro:
    def __init__(
        self,
        id: int,
        modulo: str,
        nombre: str,
        valor: str,
        tipo: Optional[str] = None,
        rango: Optional[tuple[float, float]] = None,
    ):
        self.id = id
        self.modulo = modulo
        self.nombre = nombre
        self.valor = valor
        # Tipo y rango se definen al crear; si no vienen, el tipo se infiere del valor inicial
        self.tipo = tipo or self.inferir_tipo(valor)
        self.rango = rango

    @staticmethod
    def inferir_tipo(valor: str) -> str:
        try:
            int(valor)
            return "entero"
        except ValueError:
            pass
        try:
            float(valor)
            return "decimal"
        except ValueError:
            return "texto"

    # RN-46: unicidad por módulo
    def misma_clave(self, modulo: str, nombre: str) -> bool:
        return self.modulo == modulo and self.nombre == nombre

    # RN-47: valida el valor contra el tipo y el rango definidos
    def validar_valor(self, valor: Optional[str] = None) -> None:
        valor = self.valor if valor is None else valor
        if self.tipo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo de dato no soportado: {self.tipo}")
        if self.tipo == "texto":
            if not valor.strip():
                raise ValueError("El valor del parámetro no puede estar vacío")
            return
        try:
            numero = int(valor) if self.tipo == "entero" else float(valor)
        except ValueError:
            raise ValueError(f"El valor '{valor}' no es de tipo {self.tipo}")
        if self.rango is not None:
            minimo, maximo = self.rango
            if not (minimo <= numero <= maximo):
                raise ValueError(f"El valor debe estar entre {minimo} y {maximo}")

    def to_response(self) -> dict:
        return {
            "idParametro": self.id,
            "modulo": self.modulo,
            "nombre": self.nombre,
            "valor": self.valor,
        }
