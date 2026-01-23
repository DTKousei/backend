
import sys
from unittest.mock import MagicMock

# Mocks
sys.modules['config'] = MagicMock()
sys.modules['zkteco_connection'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['requests'] = MagicMock()

class MockModel: pass
sys.modules['models'] = MagicMock()
sys.modules['models.usuario'] = MagicMock()
sys.modules['models.usuario'].Usuario = MockModel
sys.modules['models.asistencia'] = MagicMock()
sys.modules['models.asistencia'].Asistencia = MockModel
sys.modules['models.turnos'] = MagicMock()
sys.modules['models.turnos'].SegmentosHorario = MockModel
sys.modules['models.turnos'].AsignacionHorario = MockModel
sys.modules['models.turnos'].Feriados = MockModel
sys.modules['models.reportes'] = MagicMock()
sys.modules['models.reportes'].AsistenciaDiaria = MockModel
sys.modules['models.dispositivo'] = MagicMock()
sys.modules['models.dispositivo'].Dispositivo = MockModel
sys.modules['schemas'] = MagicMock()
sys.modules['schemas.asistencia'] = MagicMock()

try:
    from services.asistencia_service import AsistenciaService
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("Calling dummy method...")
    # Mock verify_incidencia to avoid complexity
    AsistenciaService.verificar_incidencia = MagicMock(return_value=(False, None))
    
    # We can't easily call procesar without db mock setup, but we'll try passing mocks
    from datetime import date
    db = MagicMock()
    # prevent crash on query
    db.query.return_value.filter.return_value.first.return_value = None # No user
    
    res = AsistenciaService.procesar_asistencia_dia(db, "1", date(2025,1,1))
    print(f"Result: {res}")
except Exception as e:
    print(f"Execution failed: {e}")
    import traceback
    traceback.print_exc()
