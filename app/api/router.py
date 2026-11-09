from typing import List
from fastapi import APIRouter, status

from app.domain.models import Product, ProductCreate
from app.services.product_service import ProductService
from app.repositories.product_repo import ProductRepository


# Instancias (en producción usarías DI de FastAPI)
repo = ProductRepository()
service = ProductService(repo)

# Router: agrupa endpoints bajo un prefijo
router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[Product])
def list_products():
    """Devuelve todos los productos."""
    return service.get_all_products()


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    """Devuelve un producto por su ID."""
    return service.get_product(product_id)


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED
)
def create_product(data: ProductCreate):
    """Crea un nuevo producto."""
    return service.create_product(data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
def delete_product(product_id: int):
    """Elimina un producto por su ID."""
    return service.delete_product(product_id)