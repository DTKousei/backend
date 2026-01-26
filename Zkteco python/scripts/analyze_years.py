import sys
import os
from sqlalchemy import func, extract

# Add parent directory to path to import from models and others
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal
from models.asistencia import Asistencia

def analyze_years():
    db = SessionLocal()
    with open("year_distribution.txt", "w") as f:
        try:
            f.write("--- Year Distribution in Asistencia ---\n")
            results = db.query(extract('year', Asistencia.timestamp).label('year'), func.count(Asistencia.id)).group_by('year').all()
            for year, count in results:
                f.write(f"Year {year}: {count} records\n")
                
        except Exception as e:
            f.write(f"Error: {e}\n")
        finally:
            db.close()
    print("Results written to year_distribution.txt")

if __name__ == "__main__":
    analyze_years()
