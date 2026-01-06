import sys
import os

# Add parent directory to path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.data_fetcher import fetch_sabana_data
import json

try:
    print("Fetching data...")
    data = fetch_sabana_data("1", "2026")
    
    with open("data_inspection.txt", "w", encoding="utf-8") as f:
        if data and "data" in data and len(data["data"]) > 0:
            emp = data["data"][0]
            f.write(f"Keys: {list(emp.keys())}\n")
            f.write("Sample Data (excluding huge lists):\n")
            f.write(json.dumps({k: v for k, v in emp.items() if k not in ["asistencia_dias", "resumen"]}, indent=2))
            f.write("\n\nSample asistencia_dias item:\n")
            f.write(str(emp["asistencia_dias"][0]))
            f.write(f"\nType: {type(emp['asistencia_dias'][0])}")
        else:
            f.write("No data returned.")
    print("Done.")

except Exception as e:
    with open("data_inspection.txt", "w", encoding="utf-8") as f:
        f.write(f"Error: {e}")
    print(f"Error: {e}")
