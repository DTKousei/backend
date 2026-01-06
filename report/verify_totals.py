import requests
import json

url = "http://localhost:8001/api/asistencias/reporte?fecha_inicio=2026-01-06&fecha_fin=2026-01-06"

try:
    print(f"Calling {url}...")
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    totales = data.get("totales", {})
    tardanzas_total = totales.get("tardanzas", 0)
    
    records = data.get("data", [])
    
    tardanzas_calc = 0
    records_with_tardanza = 0
    
    for r in records:
        t = r.get("tardanzas", 0)
        tardanzas_calc += t
        if t > 0:
            records_with_tardanza += 1
            print(f"User {r.get('user_id')} has tardanza: {t}")
            
    print("-" * 30)
    print(f"Total Tardanzas (Reported): {tardanzas_total}")
    print(f"Total Tardanzas (Calculated): {tardanzas_calc}")
    print(f"Records with Tardanza > 0: {records_with_tardanza}")
    
    if tardanzas_total == tardanzas_calc:
        print("SUCCESS: Totals match.")
    else:
        print("FAILURE: Totals mismatch.")
        
    # Check if we at least found some tardanzas (since user said there is one today)
    if records_with_tardanza > 0:
         print("Validation: At least one tardanza found as expected.")
    else:
         print("Warning: No tardanzas found in data (logic might still be failing to capture 'TARDE').")

except Exception as e:
    print(f"Error: {e}")
