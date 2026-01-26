
import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, time, timedelta

# --- MOCK MODULES BEFORE IMPORTING SERVICE ---
sys.modules['config'] = MagicMock()
sys.modules['zkteco_connection'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['sqlalchemy.ext.declarative'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Mock models explicitly to avoid import errors if DB connection is attempted at import time
mock_models = MagicMock()
sys.modules['models'] = mock_models
sys.modules['models.usuario'] = MagicMock()
sys.modules['models.asistencia'] = MagicMock()
sys.modules['models.dispositivo'] = MagicMock()
sys.modules['models.turnos'] = MagicMock()
sys.modules['models.reportes'] = MagicMock()
sys.modules['schemas'] = MagicMock()
sys.modules['schemas.asistencia'] = MagicMock()

# We need to ensure Asistencia class is available as it's used in type hinting or logic
MockUsuario = MagicMock()
MockAsistencia = MagicMock()
MockSegmentosHorario = MagicMock()
MockAsignacionHorario = MagicMock()
MockFeriados = MagicMock()
MockAsistenciaDiaria = MagicMock()
MockDispositivo = MagicMock()

sys.modules['models.usuario'].Usuario = MockUsuario
sys.modules['models.asistencia'].Asistencia = MockAsistencia
sys.modules['models.turnos'].SegmentosHorario = MockSegmentosHorario
sys.modules['models.turnos'].AsignacionHorario = MockAsignacionHorario
sys.modules['models.turnos'].Feriados = MockFeriados
sys.modules['models.reportes'].AsistenciaDiaria = MockAsistenciaDiaria
sys.modules['models.dispositivo'].Dispositivo = MockDispositivo

MockUsuario.__name__ = "Usuario"
MockAsistencia.__name__ = "Asistencia"
MockSegmentosHorario.__name__ = "SegmentosHorario"
MockAsignacionHorario.__name__ = "AsignacionHorario"
MockFeriados.__name__ = "Feriados"
MockAsistenciaDiaria.__name__ = "AsistenciaDiaria"
MockDispositivo.__name__ = "Dispositivo"

# Now import service
from services.asistencia_service import AsistenciaService

class TestAsistenciaLogic(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.user_id = "1"
        self.fecha = date(2025, 1, 9)
        
        # Mock Usuario
        self.usuario = MagicMock()
        self.usuario.uid = 123
        self.db.query().filter().first.return_value = self.usuario

        # Mock Reporte (Start fresh to avoid persistence across tests)
        self.reporte = MagicMock()
        self.reporte.horas_trabajadas = 0
        self.reporte.estado_asistencia = "INIT"
        self.reporte.fecha = self.fecha
        self.reporte.user_id = self.user_id
        
        # Requests Mock
        # ensure requests.get returns 200 and empty list by default
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        sys.modules['requests'].get.return_value = mock_response

    def setup_mocks(self, asignacion=True, feriado=False, logs=[], segmentos=None, fecha_passada=True):
        # Reset side effects
        self.db.query.return_value.filter.return_value.order_by.return_value.first.side_effect = None
        self.db.query.return_value.filter.return_value.first.side_effect = None
        self.db.query.return_value.filter.return_value.all.side_effect = None
        self.db.query.return_value.order_by.return_value.all.side_effect = None
        
        # --- SIMPLE QUERY HANDLING ---
        # Instead of complex side effects, let's just mock the chain based on call order or inspection
        # But since the service calls query(Model) multiple times, side_effect is best.
        
        def query_side_effect(model):
            # Inspect the model passed to query()
            # Since we mocked modules, model might be a Mock or our MockModel class
            model_name = str(model)
            if hasattr(model, '__name__'):
                 model_name = model.__name__
            
            # Helper for subsequent chain
            query_obj = MagicMock()
            filter_obj = MagicMock()
            order_obj = MagicMock()
            
            def return_first():
                if "Usuario" in model_name: return self.usuario
                if "AsignacionHorario" in model_name:
                    if asignacion:
                        asig = MagicMock()
                        asig.horario_id = 1
                        return asig
                    # if no assignment, returns None
                    return None
                if "Feriados" in model_name:
                    return MagicMock() if feriado else None
                if "AsistenciaDiaria" in model_name:
                    return self.reporte
                return None
                
            def return_all():
                if "SegmentosHorario" in model_name:
                    if segmentos: return segmentos
                    s1 = MagicMock(); s1.hora_inicio = time(8, 0); s1.hora_fin = time(13, 0); s1.tolerancia_minutos = 15
                    s2 = MagicMock(); s2.hora_inicio = time(14, 0); s2.hora_fin = time(17, 0); s2.tolerancia_minutos = 15
                    return [s1, s2]
                if "Asistencia" in model_name:
                    log_objs = []
                    for t in logs:
                        l = MagicMock()
                        l.timestamp = datetime.combine(self.fecha, t)
                        l.time = l.timestamp.time # Mock time method? No, timestamp is datetime
                        log_objs.append(l)
                    return log_objs
                return []
                
            query_obj.filter.return_value = filter_obj
            filter_obj.order_by.return_value = order_obj
            filter_obj.first.side_effect = return_first
            filter_obj.all.side_effect = return_all
            
            order_obj.first.side_effect = return_first
            order_obj.all.side_effect = return_all
            
            # Handle query().all() directly? No, usually filtered.
            query_obj.all.side_effect = return_all
            
            return query_obj

        self.db.query.side_effect = query_side_effect
        
        if fecha_passada:
            self.mock_now = datetime(2030, 1, 1, 12, 0)
        else:
            self.mock_now = datetime.combine(self.fecha, time(10, 0))

    @patch('services.asistencia_service.datetime') 
    @patch.object(AsistenciaService, 'verificar_incidencia')
    def test_entry_no_exit_is_falta(self, mock_incidencia, mock_datetime):
        self.setup_mocks(logs=[time(8,0)], fecha_passada=True, feriado=False)
        mock_datetime.now.return_value = datetime(2030, 1, 1)
        mock_datetime.combine = datetime.combine 
        mock_incidencia.return_value = (False, None)
        
        res = AsistenciaService.procesar_asistencia_dia(self.db, self.user_id, self.fecha)
        self.assertEqual(res.estado_asistencia, "FALTA")
        print("Test 1 OK: Entry No Exit -> FALTA")

    @patch('services.asistencia_service.datetime')
    @patch.object(AsistenciaService, 'verificar_incidencia')
    def test_feriado_overrides_falta(self, mock_incidencia, mock_datetime):
        self.setup_mocks(logs=[time(8,0)], feriado=True, fecha_passada=True)
        mock_datetime.now.return_value = datetime(2030, 1, 1)
        mock_datetime.combine = datetime.combine
        mock_incidencia.return_value = (False, None)
        
        res = AsistenciaService.procesar_asistencia_dia(self.db, self.user_id, self.fecha)
        self.assertEqual(res.estado_asistencia, "FERIADO")
        print("Test 2 OK: Feriado overrides Incomplete")

    @patch('services.asistencia_service.datetime')
    @patch.object(AsistenciaService, 'verificar_incidencia')
    def test_incidencia_overrides_falta(self, mock_incidencia, mock_datetime):
        self.setup_mocks(logs=[], feriado=False, fecha_passada=True)
        mock_datetime.now.return_value = datetime(2030, 1, 1)
        mock_datetime.combine = datetime.combine
        mock_incidencia.return_value = (True, "VAC")
        
        res = AsistenciaService.procesar_asistencia_dia(self.db, self.user_id, self.fecha)
        self.assertEqual(res.estado_asistencia, "VAC")
        print("Test 3 OK: Incidencia overrides Absence")

    @patch('services.asistencia_service.datetime')
    @patch.object(AsistenciaService, 'verificar_incidencia')
    def test_complete_work_overrides_feriado(self, mock_incidencia, mock_datetime):
        self.setup_mocks(logs=[time(8,0), time(13,0), time(14,0), time(17,0)], feriado=True, fecha_passada=True)
        mock_datetime.now.return_value = datetime(2030, 1, 1)
        mock_datetime.combine = datetime.combine
        mock_incidencia.return_value = (False, None)
        
        res = AsistenciaService.procesar_asistencia_dia(self.db, self.user_id, self.fecha)
        self.assertEqual(res.estado_asistencia, "PRESENTE")
        print("Test 4 OK: Complete work overrides Feriado")

if __name__ == '__main__':
    try:
        unittest.main(exit=False)
    except Exception as e:
        import traceback
        traceback.print_exc()
