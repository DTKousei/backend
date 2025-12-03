"""
Configuración de la base de datos y sesión de SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear el engine de SQLAlchemy con la URL de MySQL
engine = create_engine(
    settings.database_url,
    echo=settings.API_DEBUG,  # Mostrar SQL queries en modo debug
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_recycle=3600,  # Reciclar conexiones cada hora
)

# Crear SessionLocal para manejar sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency para obtener una sesión de base de datos.
    Se usa con FastAPI's Depends() para inyección de dependencias.
    
    Uso:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    Esta función debe llamarse al inicio de la aplicación.
    """
    try:
        logger.info("Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"✗ Error al crear tablas: {str(e)}")
        raise


def drop_db():
    """
    Elimina todas las tablas de la base de datos.
    ¡ADVERTENCIA! Esta función es destructiva.
    """
    try:
        logger.warning("Eliminando todas las tablas de la base de datos...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ Tablas eliminadas")
    except Exception as e:
        logger.error(f"✗ Error al eliminar tablas: {str(e)}")
        raise
