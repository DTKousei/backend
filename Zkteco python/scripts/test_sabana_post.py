import sys
import os
import json
import urllib.request
import urllib.error

def test_sabana_post():
    print("Testing POST http://localhost:8000/api/reportes/sabana...")
    
    url = "http://localhost:8000/api/reportes/sabana"

    # 1. Test basic request (no user filter)
    payload = {
        "anio": 2025,
        "mes": 12
    }
    data_json = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(url, data=data_json, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("Success! Response 200 OK")
                body = response.read().decode('utf-8')
                data = json.loads(body)
                print(f"Meta: {data.get('meta')}")
                print(f"Total empleados: {len(data.get('data', []))}")
                
                # 2. Test with user_ids filter
                empleados = data.get('data', [])
                if empleados:
                    target_user_id = empleados[0]['user_id']
                    # Ensure target_user_id is treated as string for the payload
                    target_user_id = str(target_user_id) 
                    print(f"\nTesting filter with user_id: {target_user_id}")
                    
                    payload_filter = {
                        "anio": 2025,
                        "mes": 12,
                        "user_ids": [target_user_id]
                    }
                    data_filter_json = json.dumps(payload_filter).encode('utf-8')
                    req_filter = urllib.request.Request(url, data=data_filter_json, headers={'Content-Type': 'application/json'})
                    
                    with urllib.request.urlopen(req_filter) as response_filter:
                         if response_filter.status == 200:
                            body_filter = response_filter.read().decode('utf-8')
                            data_filter = json.loads(body_filter)
                            print(f"Filtered Total empleados: {len(data_filter.get('data', []))}")
                            if len(data_filter.get('data', [])) == 1:
                                print("Filter worked correctly!")
                            else:
                                print(f"Warning: Expected 1 employee, got {len(data_filter.get('data', []))}")
            else:
                print(f"Failed: {response.status}")

    except urllib.error.URLError as e:
        print(f"Error accessing API: {e}")
        print("Ensure the API server is running on localhost:8000")

if __name__ == "__main__":
    test_sabana_post()
