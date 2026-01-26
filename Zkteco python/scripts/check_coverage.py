import sys
import os
import logging
from datetime import date, timedelta
from sqlalchemy import or_

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.turnos import AsignacionHorario
from models.usuario import Usuario
from models.database import SessionLocal

def check_coverage():
    # Silenciar logs
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    db = SessionLocal()
    target_uid = 6
    
    with open("coverage_results.txt", "w") as f:
        # 1. Buscar usuario
        user = db.query(Usuario).filter(Usuario.uid == target_uid).first()
        if not user:
            f.write("User not found\n")
            return
            
        user_id = user.user_id
        f.write(f"Checking coverage for {user_id} (UID 6) in 2025...\n")
        
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)
        
        delta = timedelta(days=1)
        curr = start_date
        
        missing_days = []
        
        try:
            while curr <= end_date:
                # Replica logic from AsistenciaService
                asignacion = db.query(AsignacionHorario).filter(
                    AsignacionHorario.user_id == user_id,
                    AsignacionHorario.fecha_inicio <= curr,
                    or_(
                        AsignacionHorario.fecha_fin == None,
                        AsignacionHorario.fecha_fin >= curr
                    )
                ).order_by(AsignacionHorario.fecha_inicio.desc()).first()
                
                if not asignacion:
                    missing_days.append(curr)
                
                curr += delta
        except Exception as e:
            f.write(f"Error during check: {e}\n")
            
        if missing_days:
            f.write(f"FAILED! Found {len(missing_days)} days without coverage:\n")
            for d in missing_days[:10]:
                f.write(f" - {d}\n")
            if len(missing_days) > 10:
                f.write("...\n")
        else:
            f.write("SUCCESS! All 365 days in 2025 have valid assignment coverage.\n")
        
    db.close()

if __name__ == "__main__":
    check_coverage()
