import unittest
from unittest.mock import patch
from services.data_fetcher import fetch_sabana_data
import os

class TestAreaPayload(unittest.TestCase):
    @patch('services.data_fetcher.requests.post')
    @patch('services.data_fetcher.fetch_incidencias') # Mock incidence fetch to avoid external call
    def test_fetch_sabana_with_area(self, mock_incidencias, mock_post):
        # Setup
        mock_incidencias.return_value = []
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {"data": []}
        mock_post.return_value = mock_response
        
        # Test call
        fetch_sabana_data(mes="1", anio="2026", area="Direccion")
        
        # Verify payload
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        
        self.assertIn('area', payload)
        self.assertEqual(payload['area'], 'Direccion')
        self.assertEqual(payload['mes'], '1')
        print("Test passed: 'area' parameter found in payload.")

if __name__ == '__main__':
    unittest.main()
