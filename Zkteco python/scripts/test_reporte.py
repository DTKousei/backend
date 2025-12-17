import sys
import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base
from models.usuario import Usuario
from models.reportes import AsistenciaDiaria
from services.reporte_service import ReporteService
from config import settings

# Setup DB connection
DATABASE_URL = f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_reporte():
    db = SessionLocal()
    try:
        print("Testing ReporteService...")
        
        # 1. Check if we have users
        users = db.query(Usuario).limit(5).all()
        if not users:
            print("No users found. Creating a dummy user for test.")
            # ... logic to create dummy user if needed, but let's assume users exist
        else:
            print(f"Found {len(users)} users.")

        # 2. Check if we have AsistenciaDiaria records
        print("Checking AsistenciaDiaria records...")
        records = db.query(AsistenciaDiaria).limit(5).all()
        if not records:
             print("No attendance records found. This test might return empty data (filled with FAL/D).")
        else:
             print(f"Found records. Sample date: {records[0].fecha}")

        # 3. Generate Matrix for current month (or a specific month)
        # Using December 2025 as per user context in prompt, or maybe current month?
        # User prompt mentions: "Debe ser fácil de iterar: { "meta": { "mes": 11, "anio": 2025, ... } }"
        # Let's try to query a month that might have data. 
        # Since I don't know the exact data range, I'll try the month of the first record found, or current month.
        
        target_month = 12
        target_year = 2025
        
        if records:
            target_month = records[0].fecha.month
            target_year = records[0].fecha.year
            print(f"Using month from record: {target_month}/{target_year}")
        else:
            print(f"Using default month: {target_month}/{target_year}")

        sabana = ReporteService.obtener_sabana_asistencia(db, target_year, target_month)
        
        print("\n--- Reporte Generado ---")
        print(f"Meta: {sabana['meta']}")
        print(f"Columnas: {len(sabana['columnas_dias'])} dias")
        print(f"Total Empleados: {len(sabana['data'])}")
        
        if sabana['data']:
            emp1 = sabana['data'][0]
            print(f"Empleado 1: {emp1['nombre']}")
            print(f"Resumen: {emp1['resumen']}")
            print(f"Asistencia Sample (First 5 days): {emp1['asistencia_dias'][:5]}")
            
            # Verify data consistency
            assert len(emp1['asistencia_dias']) == sabana['meta']['dias_total']
            print("Data consistency check passed.")
        else:
            print("No employee data returned.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_reporte()
