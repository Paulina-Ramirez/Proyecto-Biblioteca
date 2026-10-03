from fastapi import FastAPI
from app.config.database import engine, Base
from app.models import libro, usuario, prestamo, sancion

# Importar routers
from app.routers import libro_router, usuario_router, prestamo_router, sancion_router

app = FastAPI(
    title="API Biblioteca",
    description="Sistema de Gestión de Biblioteca - Arquitectura N-Tier",
    version="1.0.0"
)

# Registrar routers
app.include_router(libro_router.router)
app.include_router(usuario_router.router)
app.include_router(prestamo_router.router)
app.include_router(sancion_router.router)

@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "API Biblioteca funcionando ✅",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "ok"}