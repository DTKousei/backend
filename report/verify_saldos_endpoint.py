import requests
import os

url = "http://localhost:8001/api/reports/export/saldos-pdf"
payload = {
    "anio": 2026
    # "empleado_id": "12345678" # Optional
}

try:
    print(f"Testing POST {url} with payload {payload}...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("SUCCESS: Endpoint returned 200 OK")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        content_len = len(response.content)
        print(f"Content Length: {content_len} bytes")
        
        if content_len > 0:
            config_dir = "test_output"
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            filename = os.path.join(config_dir, "test_saldos.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Saved PDF to {filename}")
        else:
            print("WARNING: Empty content received")
            
    else:
        print(f"FAILURE: Status {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error executing request: {e}")
