import json

try:
    with open("raw_data_debug.json", "r", encoding="utf-16") as f: # PowerShell default is often utf-16
        data = json.load(f)
        
    # PowerShell ConvertTo-Json might wrap in a wrapper or just return list
    # The previous output showed "value" key, suggesting it might be wrapped or just a list.
    
    unique_statuses = set()
    
    records = data if isinstance(data, list) else data.get("value", [])
    
    for r in records:
        status = r.get("estado_asistencia")
        unique_statuses.add(f"'{status}'")
        
    print("Unique Statuses Found:", unique_statuses)
    
except Exception as e:
    print(f"Error reading utf-16: {e}")
    try:
        with open("raw_data_debug.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        unique_statuses = set()
        records = data if isinstance(data, list) else data.get("value", [])
        for r in records:
            status = r.get("estado_asistencia")
            unique_statuses.add(f"'{status}'")
        print("Unique Statuses Found (utf-8):", unique_statuses)
    except Exception as e2:
        print(f"Error reading utf-8: {e2}")
