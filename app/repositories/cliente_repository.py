# ─────────────────────────────────────────────────────────────
# CAPA REPOSITORIO — almacenamiento en memoria de clientes
# Solo guarda y recupera. Sin lógica de negocio.
# ─────────────────────────────────────────────────────────────

from typing import Optional

from app.domain.cliente import Cliente, DireccionEnvio


class ClienteRepository:

    def __init__(self):
        self._datos: list[Cliente] = []
        self._siguiente_id: int = 1
        self._seed()

    def _seed(self):
        """11 clientes de ejemplo (ids 1-11): el siguiente registro recibe el id 12."""
        iniciales = [
            ("800100200-1", "Colegio San José",       "info@sanjose.edu.co",   "Cl 36 # 20-15, Bucaramanga"),
            ("800200300-2", "Club Los Tigres",        "club@tigres.com",       "Cra 15 # 30-10, Floridablanca"),
            ("800300400-3", "Liga Santandereana",     "liga@santander.org",    "Cl 45 # 12-30, Bucaramanga"),
            ("800400500-4", "Academia Deportiva Sol", "academia@sol.com",      "Cra 27 # 50-20, Bucaramanga"),
            ("800500600-5", "Colegio La Salle",       "contacto@lasalle.edu",  "Cl 52 # 25-40, Bucaramanga"),
            ("800600700-6", "Club Atlético Norte",    "norte@atletico.com",    "Av. Quebradaseca # 10-05"),
            ("800700800-7", "Empresa Textil Andina",  "ventas@andina.com",     "Cra 33 # 41-18, Bucaramanga"),
            ("800800900-8", "Escuela de Fútbol Gol",  "gol@escuela.com",       "Cl 60 # 18-22, Girón"),
            ("800900100-9", "Colegio Los Álamos",     "info@alamos.edu.co",    "Cra 21 # 35-12, Piedecuesta"),
            ("801000200-1", "Club Voleibol Olas",     "olas@voleibol.com",     "Cl 70 # 22-14, Bucaramanga"),
            ("801100300-2", "Cooperativa Deportiva",  "coop@deportiva.com",    "Cra 19 # 28-33, Bucaramanga"),
        ]
        for nit, nombre, email, direccion in iniciales:
            self.crear(nit, nombre, email, [DireccionEnvio(direccion, principal=True)])

    def obtener_todos(self) -> list[Cliente]:
        return self._datos.copy()

    def obtener_activo_por_nit(self, nit: str) -> Optional[Cliente]:
        """Busca una cuenta ACTIVA con ese NIT (insumo de la regla RN-10)."""
        return next((c for c in self._datos if c.activo_con_nit(nit)), None)

    def crear(self, nit: str, nombre: str, email: str,
              direcciones: list[DireccionEnvio]) -> Cliente:
        nuevo = Cliente(self._siguiente_id, nit, nombre, email, direcciones)
        self._datos.append(nuevo)
        self._siguiente_id += 1
        return nuevo
    
    def obtener_por_id(self, id: int) -> Optional[Cliente]:
        """Busca un cliente por su id (lo usa MOD-01 para validar el pedido)."""
        return next((c for c in self._datos if c.id == id), None)


# Instancia única compartida (Singleton simple)
cliente_repository = ClienteRepository()