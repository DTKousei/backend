"""
Inicialización del paquete de routers
"""

from api.routers import dispositivos, usuarios, asistencias, horarios, sincronizacion

__all__ = [
    "dispositivos",
    "usuarios",
    "asistencias",
    "horarios",
    "sincronizacion"
]
