from config.database import Base, engine
from models.report_log import TipoReporte, FormatoReporte, ReporteGenerado

def reset_database():
    print("Resetting database...")
    try:
        # Drop all tables
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

        # Create all tables
        print("Creating all tables with new schema...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
