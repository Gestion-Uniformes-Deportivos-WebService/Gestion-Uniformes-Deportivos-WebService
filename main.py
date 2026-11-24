# 
# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA — ejecutar desde la raíz del proyecto:
#   uvicorn main:app --reload
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.router import router
from app.api.diseno_router import router as diseno_router
from app.api.parametro_router import router as parametro_router
from app.api.cliente_router import router as cliente_router
from app.api.pedido_router import router as pedido_router
from app.api.ficha_tecnica_router import router as ficha_tecnica_router
from app.api.inventario_router import router as inventario_router
from app.api.produccion_router import router as produccion_router
from app.api.calidad_router import router as calidad_router
from app.api.pago_router import router as pago_router
from app.core.responses import manejar_error_dominio, manejar_validacion
from app.core.manejadores import registrar_manejadores
from app.domain.errores import ErrorDominio


app = FastAPI(
    title="API Gestión de Pedidos de Uniformes Deportivos",
    description="API REST con arquitectura de capas",
    version="1.0.0"
)

# Manejadores de excepciones
app.add_exception_handler(ErrorDominio, manejar_error_dominio)
app.add_exception_handler(RequestValidationError, manejar_validacion)

registrar_manejadores(app)

# Registro de rutas
app.include_router(router)
app.include_router(diseno_router)
app.include_router(parametro_router)
app.include_router(cliente_router)
app.include_router(pedido_router)
app.include_router(ficha_tecnica_router)
app.include_router(inventario_router)
app.include_router(produccion_router)
app.include_router(calidad_router)
app.include_router(pago_router)
@app.get("/")
def root():
    return {
        "mensaje": "API corriendo correctamente 🚀",
        "docs": "http://127.0.0.1:8000/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
