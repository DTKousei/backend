"""
Script de Inicialización de Base de Datos
Crea todas las tablas necesarias en MySQL
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_db, drop_db, engine
from models import Dispositivo, Usuario, Asistencia, Horario
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Inicializa la base de datos
    """
    print("=" * 80)
    print("INICIALIZACIÓN DE BASE DE DATOS - API ZKTECO")
    print("=" * 80)
    print(f"\nBase de datos: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"Usuario: {settings.DB_USER}")
    print("\n" + "=" * 80)
    
    # Preguntar si desea eliminar tablas existentes
    respuesta = input("\n¿Desea eliminar las tablas existentes? (s/N): ").strip().lower()
    
    if respuesta == 's':
        try:
            logger.info("Eliminando tablas existentes...")
            drop_db()
            logger.info("✓ Tablas eliminadas exitosamente")
        except Exception as e:
            logger.error(f"✗ Error al eliminar tablas: {str(e)}")
            return
    
    # Crear tablas
    try:
        logger.info("\nCreando tablas...")
        init_db()
        logger.info("✓ Tablas creadas exitosamente")
        
        # Mostrar tablas creadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        
        print("\n" + "=" * 80)
        print("TABLAS CREADAS:")
        print("=" * 80)
        for tabla in tablas:
            print(f"  ✓ {tabla}")
        
        print("\n" + "=" * 80)
        print("INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print("\nLa base de datos está lista para usar.")
        print("Puede iniciar la API con: python scripts/run_api.py")
        
    except Exception as e:
        logger.error(f"\n✗ Error al crear tablas: {str(e)}")
        logger.error("\nVerifique que:")
        logger.error("  1. MySQL esté ejecutándose")
        logger.error("  2. Las credenciales en .env sean correctas")
        logger.error(f"  3. La base de datos '{settings.DB_NAME}' exista")
        logger.error("\nPuede crear la base de datos con:")
        logger.error(f"  mysql -u {settings.DB_USER} -p -e \"CREATE DATABASE {settings.DB_NAME};\"")
        sys.exit(1)


if __name__ == "__main__":
    main()
