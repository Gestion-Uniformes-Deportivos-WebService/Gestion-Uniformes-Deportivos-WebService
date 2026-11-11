# ─────────────────────────────────────────────────────────────
# CAPA REPOSITORIO — almacenamiento en memoria de parámetros
# Solo guarda y recupera. Sin lógica de negocio.
# ─────────────────────────────────────────────────────────────

from typing import Optional

from app.domain.parametro import Parametro


class ParametroRepository:

    def __init__(self):
        self._datos: list[Parametro] = []
        self._siguiente_id: int = 1
        self._seed()

    def _seed(self):
        """Parámetros iniciales (ids 1-6). El siguiente registro recibe el id 7."""
        iniciales = [
            ("MOD-01", "PORCENTAJE_ANTICIPO", "50"),
            ("MOD-01", "DIAS_VIGENCIA_COTIZACION", "15"),
            ("MOD-03", "DIAS_PRODUCCION_ESTIMADO", "10"),
            ("MOD-05", "MONEDA", "COP"),
            ("MOD-05", "IVA_PORCENTAJE", "19"),
            ("MOD-08", "ZONA_HORARIA", "America/Bogota"),
        ]
        for modulo, nombre, valor in iniciales:
            self.crear(modulo, nombre, valor)

    def obtener_todos(self) -> list[Parametro]:
        return self._datos.copy()

    def obtener_por_modulo_y_nombre(self, modulo: str, nombre: str) -> Optional[Parametro]:
        return next((p for p in self._datos if p.misma_clave(modulo, nombre)), None)

    def crear(self, modulo: str, nombre: str, valor: str,
              tipo: Optional[str] = None,
              rango: Optional[tuple[float, float]] = None) -> Parametro:
        nuevo = Parametro(self._siguiente_id, modulo, nombre, valor, tipo, rango)
        self._datos.append(nuevo)
        self._siguiente_id += 1
        return nuevo


# Instancia única compartida (Singleton simple)
parametro_repository = ParametroRepository()
