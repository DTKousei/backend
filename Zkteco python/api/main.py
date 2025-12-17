"""
Aplicación principal de FastAPI
API REST para gestión de dispositivos ZKTeco
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models.database import init_db
import logging

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers
from api.routers import dispositivos, usuarios, asistencias, horarios, sincronizacion, reportes

# Incluir routers
app.include_router(dispositivos.router)
app.include_router(usuarios.router)
app.include_router(asistencias.router)
app.include_router(horarios.router)
app.include_router(sincronizacion.router)
app.include_router(reportes.router)


@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación
    """
    logger.info("Iniciando API ZKTeco...")
    logger.info(f"Versión: {settings.API_VERSION}")
    logger.info(f"Base de datos: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    # Inicializar base de datos
    try:
        init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento que se ejecuta al cerrar la aplicación
    """
    logger.info("Cerrando API ZKTeco...")


@app.get("/")
def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "API REST ZKTeco",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """
    Endpoint de health check
    """
    return {
        "status": "healthy",
        "timestamp": str(datetime.now())
    }


if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )
