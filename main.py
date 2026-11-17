from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.router import router
from app.api.diseno_router import router as diseno_router
from app.core.responses import manejar_error_dominio, manejar_validacion
from app.domain.errores import ErrorDominio

app = FastAPI(
    title="API Gestión de Pedidos de Uniformes Deportivos",
    description="API REST con arquitectura de capas",
    version="1.0.0"
)

app.add_exception_handler(ErrorDominio, manejar_error_dominio)
app.add_exception_handler(RequestValidationError, manejar_validacion)

app.include_router(router)
app.include_router(diseno_router)


@app.get("/")
def root():
    return {"message": "¡API funcionando! 🚀"}