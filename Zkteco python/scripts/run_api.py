"""
Script para ejecutar la API
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from config import settings


def main():
    """
    Ejecuta la API con uvicorn
    """
    print("=" * 80)
    print("INICIANDO API REST ZKTECO")
    print("=" * 80)
    print(f"\nTítulo: {settings.API_TITLE}")
    print(f"Versión: {settings.API_VERSION}")
    print(f"Host: {settings.API_HOST}:{settings.API_PORT}")
    print(f"Debug: {settings.API_DEBUG}")
    print("\n" + "=" * 80)
    print("\nDocumentación disponible en:")
    print(f"  Swagger UI: http://localhost:{settings.API_PORT}/docs")
    print(f"  ReDoc: http://localhost:{settings.API_PORT}/redoc")
    print("\n" + "=" * 80)
    print("\nPresione Ctrl+C para detener el servidor")
    print("=" * 80 + "\n")
    
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
