import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import settings

def update_schema():
    print("Connecting to database...")
    engine = create_engine(settings.database_url)
    
    commands = [
        "ALTER TABLE usuarios ADD COLUMN fecha_nacimiento DATE NULL COMMENT 'Fecha de nacimiento'",
        "ALTER TABLE usuarios ADD COLUMN direccion VARCHAR(255) NULL COMMENT 'Dirección del usuario'",
        "ALTER TABLE usuarios ADD COLUMN comentarios VARCHAR(500) NULL COMMENT 'Comentarios adicionales'"
    ]
    
    with engine.connect() as connection:
        for cmd in commands:
            try:
                print(f"Executing: {cmd}")
                connection.execute(text(cmd))
                print("Success")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("Column already exists, skipping.")
                else:
                    print(f"Error executing command: {e}")
                    # Allow partial failure if some columns exist but others don't
        
        connection.commit()
    print("Schema update completed.")

if __name__ == "__main__":
    try:
        update_schema()
        sys.exit(0)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)
