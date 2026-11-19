# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — Cliente (MOD-02 / SUB-04)
# RN-09: no se registra un cliente sin documento/NIT válido.
# RN-10: no pueden existir dos cuentas activas con el mismo NIT.
# RN-12: todo cliente debe tener al menos una dirección de envío.
# No importa nada de FastAPI ni de almacenamiento.
# ─────────────────────────────────────────────────────────────

import re

from pydantic import BaseModel, Field, field_validator

# NIT o cédula: 6 a 10 dígitos, con dígito de verificación opcional (900123456-7)
PATRON_NIT = re.compile(r"^\d{6,10}(-\d)?$")
# Correo con formato básico: algo@dominio.ext
PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ── RN-09: validación del documento/NIT ───────────────────────
def documento_valido(nit: str) -> bool:
    return bool(PATRON_NIT.match((nit or "").strip()))


# ── Schema de ENTRADA (body del POST) ─────────────────────────
class ClienteCreate(BaseModel):
    nit: str = Field(..., description="NIT o documento del cliente")
    nombre: str = Field(..., description="Razón social o nombre")
    email: str = Field(..., description="Correo electrónico de contacto")
    direccion: str = Field(..., description="Dirección de envío")

    @field_validator("nit")
    @classmethod
    def nit_valido(cls, v: str) -> str:
        v = v.strip()
        if not documento_valido(v):  # RN-09
            raise ValueError("Documento/NIT no válido")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 150:
            raise ValueError("El campo nombre debe tener entre 2 y 150 caracteres")
        return v

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if not PATRON_EMAIL.match(v):
            raise ValueError("El campo email no tiene un formato válido")
        return v

    @field_validator("direccion")
    @classmethod
    def direccion_valida(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("El campo direccion debe tener al menos 5 caracteres")
        return v


# ── Schema de SALIDA (data del JSON) ──────────────────────────
class ClienteResponse(BaseModel):
    idCliente: int
    nit: str
    nombre: str
    estado: str


# ── Entidad: dirección de envío ───────────────────────────────
class DireccionEnvio:
    def __init__(self, direccion: str, principal: bool = False):
        self.direccion = direccion
        self.principal = principal

    def es_valida(self) -> bool:
        return bool(self.direccion and self.direccion.strip())


# ── Entidad: cliente ──────────────────────────────────────────
class Cliente:
    ESTADO_ACTIVO = "ACTIVO"

    def __init__(self, id: int, nit: str, nombre: str, email: str,
                 direcciones: list[DireccionEnvio], estado: str = ESTADO_ACTIVO):
        self.id = id
        self.nit = nit
        self.nombre = nombre
        self.email = email
        self.direcciones = direcciones
        self.estado = estado

    def esta_activo(self) -> bool:
        return self.estado == self.ESTADO_ACTIVO

    # RN-10: ¿es una cuenta activa con este NIT?
    def activo_con_nit(self, nit: str) -> bool:
        return self.esta_activo() and self.nit == nit

    # RN-12: debe existir al menos una dirección de envío válida
    def validar_direccion_envio(self) -> None:
        if not any(d.es_valida() for d in self.direcciones):
            raise ValueError("El cliente debe tener al menos una dirección de envío")

    def to_response(self) -> dict:
        return {
            "idCliente": self.id,
            "nit": self.nit,
            "nombre": self.nombre,
            "estado": self.estado,
        }