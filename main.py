# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA — ejecutar desde la raíz del proyecto:
#   uvicorn app.main:app --reload
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI

from app.api.parametro_router import router as parametro_router
from app.core.manejadores import registrar_manejadores

app = FastAPI(
    title="API Pedidos de Uniformes Deportivos",
    description="API REST con arquitectura de capas — FastAPI",
    version="1.0.0",
)

registrar_manejadores(app)

app.include_router(parametro_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "API corriendo correctamente 🚀",
        "docs": "http://127.0.0.1:8000/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
