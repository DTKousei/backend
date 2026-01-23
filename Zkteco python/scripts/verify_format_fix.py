import requests
import json
import sys

def verify_format():
    url = "http://localhost:8000/api/asistencias/reporte"
    params = {
        "fecha_inicio": "2026-01-15",
        "fecha_fin": "2026-01-15"
    }
    
    try:
        print(f"Calling GET {url} for 2026-01-15...")
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                print("No records found.")
                return

            # Print first record raw
            print("\nFirst Record Keys:")
            first = data[0]
            print(json.dumps(list(first.keys()), indent=2))
            
            print("\nValues:")
            print(f"horas_trabajadas: {first.get('horas_trabajadas')}")
            print(f"horas_trabajadas_formato: {first.get('horas_trabajadas_formato')}")
            
            if 'horas_trabajadas_formato' in first and first['horas_trabajadas_formato'] is not None:
                 print("\nSUCCESS: Field exists.")
            else:
                 print("\nFAILURE: Field missing.")
        else:
            print(response.text)
            
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    verify_format()
