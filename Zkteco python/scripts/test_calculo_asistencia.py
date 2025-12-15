import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal, init_db
from models.usuario import Usuario
from models.horario import Horario
from models.turnos import SegmentosHorario, AsignacionHorario
from models.asistencia import Asistencia
from services.asistencia_service import AsistenciaService
from services.horario_service import HorarioService
from schemas.horario import SegmentoHorarioCreate, AsignacionHorarioCreate, HorarioCreate
from datetime import date, datetime, time, timedelta

def test_calculo():
    db = SessionLocal()
    try:
        print("Creando datos de prueba...")
        
        # 1. Crear Usuario
        user = db.query(Usuario).filter(Usuario.user_id == '9999').first()
        if not user:
            from models.dispositivo import Dispositivo
            dev = db.query(Dispositivo).first()
            if not dev:
                print("No hay dispositivos, creando uno dummy")
                dev = Dispositivo(nombre="TestDev", ip_address="1.1.1.1", puerto=4370)
                db.add(dev)
                db.commit()
            
            user = Usuario(user_id='9999', nombre='Usuario Test', dispositivo_id=dev.id)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 2. Crear Horario "Mañana y Tarde"
        horario = db.query(Horario).filter(Horario.nombre == 'Horario Test Partido').first()
        if not horario:
            # Note: HorarioCreate schema doesn't have old fields anymore, good.
            # But Horario model constructor in Service might still use them if I didn't update Service?
            # I updated Service.
            h_schema = HorarioCreate(nombre='Horario Test Partido', descripcion='Turno partido')
            horario = HorarioService.crear_horario(db, h_schema)
        
        # 3. Crear Segmentos
        # Lunes (0)
        # Mañana: 08:00 - 13:00
        # Tarde: 14:00 - 18:00
        existing_segs = HorarioService.obtener_segmentos(db, horario.id)
        if not existing_segs:
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

        # 4. Asignar Horario
        assign = db.query(AsignacionHorario).filter(AsignacionHorario.usuario_id == user.id).first()
        if not assign:
            ag = AsignacionHorarioCreate(
                usuario_id=user.id, horario_id=horario.id, 
                fecha_inicio=datetime(2025, 1, 1) # Must pass datetime, model converts if needed or is date
                # Model is Date, schema is datetime. Service dumps model.
                # SQLA handles Date from datetime usually.
            )
            HorarioService.asignar_horario(db, ag)
            
        # 5. Insertar Logs (Simular marcación)
        # Fecha prueba: próximo Lunes
        fecha_prueba = date(2025, 1, 6) # Jan 6 2025 is Monday
        
        # Logs: Entrada 08:14 (OK, tolerancia 15), Salida 13:00 (OK), Entrada 14:10 (OK), Salida 18:00 (OK)
        logs = [
            datetime.combine(fecha_prueba, time(8, 14)),
            datetime.combine(fecha_prueba, time(13, 0)),
            datetime.combine(fecha_prueba, time(14, 10)),
            datetime.combine(fecha_prueba, time(18, 0))
        ]
        
        for ts in logs:
            exists = db.query(Asistencia).filter(
                Asistencia.user_id == user.user_id, 
                Asistencia.timestamp == ts
            ).first()
            if not exists:
                a = Asistencia(user_id=user.user_id, dispositivo_id=user.dispositivo_id, timestamp=ts)
                db.add(a)
        db.commit()
        
        print(f"Procesando asistencia para {fecha_prueba}...")
        reporte = AsistenciaService.procesar_asistencia_dia(db, user.id, fecha_prueba)
        
        print("-" * 50)
        print(f"Estado: {reporte.estado_asistencia}")
        print(f"Horas Esperadas: {reporte.horas_esperadas}")
        print(f"Horas Trabajadas: {reporte.horas_trabajadas}")
        print(f"Entrada Real: {reporte.entrada_real}")
        print(f"Salida Real: {reporte.salida_real}")
        print("-" * 50)
        
        assert reporte.horas_trabajadas > 7.9, f"Debería tener ~8.8 horas, tiene {reporte.horas_trabajadas}"
        print("TEST PASSED!")

    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_calculo()
