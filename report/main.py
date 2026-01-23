from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import reports, report_types
from config.database import Base, engine
import os

# Crear tablas de la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Report Service")

# Configuración de CORS
origins = ["*"] # Ajustar a ["http://localhost:5173"] para mayor seguridad en producción

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas del módulo de reportes
app.include_router(reports.router)
app.include_router(report_types.router)
from routers import system
app.include_router(system.router, prefix="/api/system", tags=["System"])
from routers import attendance
app.include_router(attendance.router)

@app.on_event("startup")
def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Verifica la conexión a la base de datos.
    """
    try:
        # Verificar conexión
        with engine.connect() as connection:
            print("\n" + "="*40)
            print(" EXITO: CONEXION A BASE DE DATOS CORRECTA ")
            print("="*40 + "\n")
    except Exception as e:
        print("\n" + "="*40)
        print(f" ERROR: NO SE PUDO CONECTAR A LA BASE DE DATOS: {e}")
        print("="*40 + "\n")

# Main entry point - Reload Triggered
if __name__ == "__main__":
    import uvicorn
    # Iniciar el servidor Uvicorn en el puerto 8001
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
