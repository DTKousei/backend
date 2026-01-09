import sys
import os
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Agregar directorio raiz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from models.database import Base
# Importar modelos para asegurar que el metadata los conozca todos con su nueva estructura
from models.usuario import Usuario
from models.asistencia import Asistencia
from models.dispositivo import Dispositivo

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_database():
    """
    Script de migración segura.
    1. Agrega índice único a `usuarios.uid`.
    2. Migra `asistencias` para usar `uid` (int) en vez de `user_id` (str).
    """
    logger.info("Iniciando migración de base de datos...")
    
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    inspector = inspect(engine)
    
    try:
        with engine.connect() as conn:
            # Deshabilitar checks FK
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            # ---------------------------------------------------------
            # PASO 1: Asegurar Índices en Tabla Usuarios
            # ---------------------------------------------------------
            logger.info("PASO 1: Verificando índices en Usuarios")
            # En MySQL, añadir índice único a columna existente es directo
            try:
                # Intentar crear índice si no existe. 
                # Nota: Es difícil chequear existencia de index de forma portatil en raw sql,
                # asi que intentamos crearlo y capturamos error si ya existe o lo hacemos idempotente.
                # O mejor, usamos SQL directo que suele fallar si existe.
                
                # Verificar si ya existe el index unique
                indexes = inspector.get_indexes('usuarios')
                uid_index_exists = any(idx['name'] == 'ux_usuarios_uid' or 'uid' in idx['column_names'] for idx in indexes)
                
                if not uid_index_exists:
                    logger.info("Creando índice UNIQUE en usuarios.uid...")
                    # Asegurar que no hay nulos o duplicados antes? asumo data limpia o manejo error
                    conn.execute(text("ALTER TABLE usuarios ADD UNIQUE INDEX ux_usuarios_uid (uid);"))
                else:
                    logger.info("El índice en usuarios.uid ya parece existir.")
                    
            except Exception as e:
                logger.warning(f"Advertencia en index usuarios: {e}")

            # ---------------------------------------------------------
            # PASO 2: Migrar Tabla Asistencias
            # ---------------------------------------------------------
            logger.info("PASO 2: Migrando tabla Asistencias (User ID -> UID)")
            
            # Verificar si existe la tabla asistencias
            if inspector.has_table("asistencias"):
                columns = [c['name'] for c in inspector.get_columns("asistencias")]
                
                if "uid" in columns:
                    logger.info("La tabla asistencias ya tiene columna 'uid'. ¿Ya fue migrada?")
                    # Aun asi podriamos querer asegurar el FK, pero asumimos que si tiene uid ya esta ok.
                    # O tal vez es una migracion parcial.
                    logger.info("Saltando recreación de tabla asistencias.")
                else:
                    # Renombrar tabla actual
                    logger.info("Renombrando tabla asistencias a asistencias_old...")
                    conn.execute(text("DROP TABLE IF EXISTS asistencias_old;"))
                    conn.execute(text("RENAME TABLE asistencias TO asistencias_old;"))
                    
                    # Crear NUEVA tabla usando los modelos de SQLAlchemy actualizados
                    logger.info("Creando nueva tabla asistencias con esquema actualizado...")
                    # create_all solo crea tablas que no existen
                    Base.metadata.create_all(bind=engine) # Esto creará 'asistencias' nueva con columna UID
                    
                    # Migrar datos
                    logger.info("Copiando datos y mapeando UserID -> UID...")
                    
                    # Query de migración masiva
                    migration_sql = """
                    INSERT INTO asistencias (uid, dispositivo_id, timestamp, status, punch, sincronizado, fecha_sincronizacion, fecha_creacion)
                    SELECT 
                        u.uid, 
                        a.dispositivo_id, 
                        a.timestamp, 
                        a.status, 
                        a.punch, 
                        a.sincronizado, 
                        a.fecha_sincronizacion, 
                        a.fecha_creacion
                    FROM asistencias_old a
                    JOIN usuarios u ON a.user_id = u.user_id
                    WHERE u.uid IS NOT NULL;
                    """
                    
                    result = conn.execute(text(migration_sql))
                    rows_migrated = result.rowcount
                    logger.info(f"✓ Se migraron {rows_migrated} registros exitosamente.")
                    
                    # Verificar si hubo registros perdidos (sin UID asociado)
                    count_old = conn.execute(text("SELECT COUNT(*) FROM asistencias_old")).scalar()
                    if rows_migrated < count_old:
                        lost = count_old - rows_migrated
                        logger.warning(f"⚠ {lost} registros no se pudieron migrar porque el usuario no tenía UID o no existía en tabla usuarios.")
                    
                    # Commit de los datos
                    conn.commit()
            
            # Habilitar checks FK
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()
            logger.info("Migración completada exitosamente.")
            
    except Exception as e:
        logger.error(f"FATAL ERROR durante la migración: {e}")
        # Intentar rollback si es posible (aunque DDL en mysql no es transaccional siempre)
        raise

if __name__ == "__main__":
    confirm = input("ADVERTENCIA: ¿Estás seguro de que quieres migrar la BD? Esto modificará tablas y datos. (s/n): ")
    if confirm.lower() == 's':
        migrate_database()
    else:
        print("Migración cancelada.")
