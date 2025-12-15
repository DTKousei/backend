import requests
import sys
import json
import random

BASE_URL = "http://localhost:8000/api"

def test_new_fields():
    # Make a random user_id to avoid collisions
    rnd_id = str(random.randint(10000, 99999))
    user_data = {
        "user_id": rnd_id,
        "nombre": f"Test User {rnd_id}",
        "privilegio": 0,
        "dispositivo_id": 1,
        "fecha_nacimiento": "1990-01-01",
        "direccion": "Av. Test 123",
        "comentarios": "Comentario inicial"
    }

    print(f"1. Creating user with new fields: {user_data['user_id']}")
    try:
        # Note: We append Sincronizar=false to avoid calling the real device if not available
        response = requests.post(f"{BASE_URL}/usuarios/?sincronizar=false", json=user_data)
        if response.status_code != 201:
            print(f"FAILED to create user: {response.status_code}")
            print(response.text)
            return False
            
        created_user = response.json()
        print("User created.")
        
        # Verify fields in creation response
        if (created_user.get('fecha_nacimiento') != user_data['fecha_nacimiento'] or
            created_user.get('direccion') != user_data['direccion'] or
            created_user.get('comentarios') != user_data['comentarios']):
            print("FAILED: Response matches inputs mismatch")
            print(json.dumps(created_user, indent=2))
            return False
            
        user_db_id = created_user['id']
        
        print(f"2. Updating user {user_db_id}...")
        update_data = {
            "direccion": "Av. Updated 456",
            "comentarios": "Comentario actualizado"
        }
        response = requests.put(f"{BASE_URL}/usuarios/{user_db_id}?sincronizar=false", json=update_data)
        if response.status_code != 200:
            print(f"FAILED to update user: {response.status_code}")
            return False
            
        updated_user = response.json()
        if (updated_user.get('direccion') != update_data['direccion'] or
            updated_user.get('comentarios') != update_data['comentarios']):
            print("FAILED: Update mismatch")
            return False
            
        print("3. Verifying with GET...")
        response = requests.get(f"{BASE_URL}/usuarios/{user_db_id}")
        get_user = response.json()
        if get_user.get('direccion') != update_data['direccion']:
            print("FAILED: GET mismatch")
            return False
            
        print("4. Deleting user...")
        response = requests.delete(f"{BASE_URL}/usuarios/{user_db_id}?eliminar_de_dispositivo=false")
        if response.status_code != 204:
            print("FAILED to delete")
            return False
            
        print("SUCCESS: All tests passed!")
        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    if test_new_fields():
        sys.exit(0)
    else:
        sys.exit(1)
