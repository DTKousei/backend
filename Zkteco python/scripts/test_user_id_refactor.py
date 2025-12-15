import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal, init_db, drop_db
from models.usuario import Usuario
from models.horario import Horario
from models.turnos import SegmentosHorario, AsignacionHorario
from models.asistencia import Asistencia
from services.asistencia_service import AsistenciaService
from services.horario_service import HorarioService
from schemas.horario import SegmentoHorarioCreate, AsignacionHorarioCreate, HorarioCreate
from datetime import date, datetime, time, timedelta

def test_calculo_user_id():
    # 1. Reset Database to apply new FKs
    print("Reseteando BD para aplicar nuevos FKs...")
    drop_db()
    init_db()
    
    db = SessionLocal()
    try:
        print("Creando datos de prueba...")
        
        # 1. Crear Usuario
        # user_id must be string and unique
        from models.dispositivo import Dispositivo
        dev = Dispositivo(nombre="TestDev", ip_address="1.1.1.1", puerto=4370)
        db.add(dev)
        db.commit()
        
        user_id_str = "9999"
        user = Usuario(user_id=user_id_str, nombre='Usuario Test', dispositivo_id=dev.id)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Crear Horario
        h_schema = HorarioCreate(nombre='Horario Test Partido', descripcion='Turno partido')
        horario = HorarioService.crear_horario(db, h_schema)
        
        # 3. Crear Segmentos
        seg1 = SegmentoHorarioCreate(
            dia_semana=0, hora_inicio=time(8,0), hora_fin=time(13,0), 
            tolerancia_minutos=15, orden_turno=1, horario_id=horario.id
        )
        seg2 = SegmentoHorarioCreate(
            dia_semana=0, hora_inicio=time(14,0), hora_fin=time(18,0), 
            tolerancia_minutos=15, orden_turno=2, horario_id=horario.id
        )
        HorarioService.crear_segmento(db, seg1)
        HorarioService.crear_segmento(db, seg2)

        # 4. Asignar Horario (Using user_id string)
        ag = AsignacionHorarioCreate(
            user_id=user_id_str, # Using string now
            horario_id=horario.id, 
            fecha_inicio=datetime(2025, 1, 1)
        )
        HorarioService.asignar_horario(db, ag)
            
        # 5. Insertar Logs (Simular marcación)
        fecha_prueba = date(2025, 1, 6) # Lunes
        
        logs = [
            datetime.combine(fecha_prueba, time(8, 5)),
            datetime.combine(fecha_prueba, time(13, 0)),
            datetime.combine(fecha_prueba, time(14, 10)),
            datetime.combine(fecha_prueba, time(18, 0))
        ]
        
        for ts in logs:
            # Asistencia now links via user_id FK
            a = Asistencia(user_id=user_id_str, dispositivo_id=dev.id, timestamp=ts)
            db.add(a)
        db.commit()
        
        print(f"Procesando asistencia para {fecha_prueba}...")
        # Service now expects user_id string
        reporte = AsistenciaService.procesar_asistencia_dia(db, user_id_str, fecha_prueba)
        
        print("-" * 50)
        print(f"User ID: {reporte.user_id}")
        print(f"Estado: {reporte.estado_asistencia}")
        print(f"Horas Trabajadas: {reporte.horas_trabajadas}")
        print("-" * 50)
        
        assert reporte.horas_trabajadas > 7.9, f"Esperado ~9, tiene {reporte.horas_trabajadas}"
        print("TEST PASSED WITH USER_ID STRING!")

    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_calculo_user_id()
