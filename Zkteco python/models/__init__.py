"""
Inicialización del paquete de modelos
Importa todos los modelos para que SQLAlchemy los reconozca
"""

from models.database import Base, get_db, init_db, drop_db
from models.dispositivo import Dispositivo
from models.usuario import Usuario
from models.asistencia import Asistencia
from models.horario import Horario

__all__ = [
    "Base",
    "get_db",
    "init_db",
    "drop_db",
    "Dispositivo",
    "Usuario",
    "Asistencia",
    "Horario",
]
