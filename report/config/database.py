import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener credenciales de la base de datos
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "reports")

# Construir la URL de conexión para SQLAlchemy
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos declarativos
Base = declarative_base()

def get_db():
    """
    Dependencia para obtener una sesión de base de datos.
    Cierra la sesión automáticamente al terminar la petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
