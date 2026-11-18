from typing import Optional, List
from app.domain.models import Product, ProductCreate


class ProductRepository:
    """Simulamos una base de datos con un dict."""

    def __init__(self):
        # "Base de datos" en memoria
        self._db: dict[int, Product] = {}
        self._next_id: int = 1

    def get_all(self) -> List[Product]:
        return list(self._db.values())

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self._db.get(product_id)

    def create(self, data: ProductCreate) -> Product:
        product = Product(id=self._next_id, **data.model_dump())
        self._db[self._next_id] = product
        self._next_id += 1
        return product

    def delete(self, product_id: int) -> bool:
        if product_id in self._db:
            del self._db[product_id]
            return True
        return False