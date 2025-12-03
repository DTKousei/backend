"""
Configuración centralizada de la aplicación
Carga variables de entorno y proporciona configuración para toda la aplicación
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Las variables se cargan automáticamente desde el archivo .env
    """
    
    # Configuración de Base de Datos
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "zkteco_db"
    
    # Configuración de la API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    API_TITLE: str = "ZKTeco API REST"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = """
    API REST para gestión de dispositivos ZKTeco de control de asistencia.
    
    Funcionalidades:
    - Gestión de dispositivos ZKTeco
    - Gestión de usuarios
    - Obtención de registros de asistencia (tiempo real y por lotes)
    - Gestión de horarios
    - Sincronización automática
    """
    
    # Configuración de CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # Configuración de Sincronización
    AUTO_SYNC_ENABLED: bool = True
    AUTO_SYNC_INTERVAL: int = 300  # 5 minutos
    
    # Configuración de Logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/api.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def database_url(self) -> str:
        """
        Construye la URL de conexión a MySQL
        """
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convierte la cadena de orígenes CORS en una lista
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Instancia global de configuración
settings = Settings()


# Crear directorio de logs si no existe
os.makedirs("logs", exist_ok=True)
