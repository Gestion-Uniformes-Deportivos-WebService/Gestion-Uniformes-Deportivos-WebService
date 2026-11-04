from fastapi import FastAPI

app = FastAPI(
    title="Gestion Uniformes Deportivos",
    description="Web Service para la gestión de uniformes deportivos",
    version="1.0.0"
)

@app.get("/")
def inicio():
    return {"mensaje": "Web Service funcionando correctamente"}

@app.get("/health")
def health_check():
    return {"status": "ok"}