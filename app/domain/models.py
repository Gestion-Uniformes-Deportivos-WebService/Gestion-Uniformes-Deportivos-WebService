from pydantic import BaseModel
from typing import Optional


# ── Modelo base: campos comunes ──────────────────
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int


# ── Para CREAR un producto (sin ID) ─────────────
class ProductCreate(ProductBase):
    pass


# ── Respuesta completa (con ID) ──────────────────
class Product(ProductBase):
    id: int

    class Config:
        # Permite leer datos desde atributos de objeto
        from_attributes = True