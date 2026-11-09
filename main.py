from fastapi import FastAPI
from app.api.router import router


# Crea la aplicación FastAPI
app = FastAPI(
    title="Mi API de Productos",
    description="API REST con arquitectura de capas",
    version="1.0.0"
)

# Registra el router de productos
app.include_router(router)


# Endpoint raíz de bienvenida
@app.get("/")
def root():
    return {"message": "¡API funcionando! 🚀"}