import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from services.data_fetcher import fetch_sabana_data, is_date_in_range

class TestIncidenceIntegration(unittest.TestCase):
    
    def test_date_range_check(self):
        # Target: 2026-01-07
        # Range: 2026-01-06 to 2026-01-13
        self.assertTrue(is_date_in_range("2026-01-07", "2026-01-06T00:00:00.000Z", "2026-01-13T00:00:00.000Z"))
        
        # Out of range
        self.assertFalse(is_date_in_range("2026-01-14", "2026-01-06T00:00:00.000Z", "2026-01-13T00:00:00.000Z"))
        
    @patch('services.data_fetcher.requests.get')
    @patch('services.data_fetcher.requests.post')
    def test_fetch_sabana_with_incidences(self, mock_post, mock_get):
        # 1. Mock Sabana Response (Attendance Data)
        # Employee with ID "12345678", January 2026.
        # Day 7 (index 6) is "FAL".
        mock_sabana_response = {
            "data": [
                {
                    "user_id": "12345678",
                    "nombre": "Juan Perez",
                    "asistencia_dias": ["A", "A", "A", "A", "A", "A", "FAL", "A"] + ["A"]*23 # 7th day is FAL
                }
            ],
            "meta": {"mes": "1", "anio": "2026"}
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_sabana_response
        
        # 2. Mock Incidences Response
        # Approved incidence for "12345678" overlapping Jan 7th.
        mock_incidences_response = {
            "data": [
                {
                    "empleado_id": "12345678",
                    "fecha_inicio": "2026-01-06T00:00:00.000Z",
                    "fecha_fin": "2026-01-13T00:00:00.000Z",
                    "estado": { "nombre": "Aprobado" },
                    "tipo_incidencia": { "codigo": "PM001" }
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_incidences_response
        
        # 3. Call Function
        result = fetch_sabana_data("1", "2026", user_ids=["12345678"])
        
        # 4. Verify Result
        employee = result["data"][0]
        # Index 6 (Day 7) should be 'PM001' now, not 'FAL'
        self.assertEqual(employee["asistencia_dias"][6], "PM001", "Absence should be justified with incidence code")
        
        print("SUCCESS: Absence was correctly justified by incidence.")

if __name__ == '__main__':
    unittest.main()
