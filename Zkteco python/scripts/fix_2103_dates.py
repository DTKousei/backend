import sys
import os

# Add parent directory to path to import from models and others
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.asistencia import Asistencia
from sqlalchemy import extract

def fix_future_dates():
    db: Session = SessionLocal()
    try:
        print("--- Fixing Future Dates (Year > 2050) ---")
        
        # Find records
        bad_records = db.query(Asistencia).filter(extract('year', Asistencia.timestamp) > 2050).all()
        count = len(bad_records)
        
        print(f"Found {count} records with invalid future dates.")
        
        if count > 0:
            print("Deleting these records...")
            # Ideally we might want to ask confirmation, but for this script we will just DO IT
            # Since this is a "fix" script, run by intention.
            
            db.query(Asistencia).filter(extract('year', Asistencia.timestamp) > 2050).delete(synchronize_session=False)
            db.commit()
            print("Records deleted successfully.")
        else:
            print("No bad records found.")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_future_dates()
