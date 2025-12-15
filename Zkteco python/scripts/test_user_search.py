import requests
import sys
import json

BASE_URL = "http://localhost:8000/api"

def test_user_search():
    print("1. Getting list of users...")
    try:
        response = requests.get(f"{BASE_URL}/usuarios/")
        if response.status_code != 200:
            print(f"Failed to get users: {response.status_code}")
            return False
            
        users = response.json()
        if not users:
            print("No users found in database to test with.")
            return True
            
        test_user = users[0]
        user_id = test_user['user_id']
        print(f"Found user with user_id: {user_id}")
        
        print(f"2. Testing search by user_id: {user_id}...")
        response = requests.get(f"{BASE_URL}/usuarios/user_id/{user_id}")
        
        if response.status_code == 200:
            found_user = response.json()
            if found_user['user_id'] == user_id:
                print("SUCCESS: User found and IDs match!")
                print(json.dumps(found_user, indent=2))
                return True
            else:
                print("FAILURE: User found but ID mismatch!")
                return False
        else:
            print(f"FAILURE: Endpoint returned {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    if test_user_search():
        sys.exit(0)
    else:
        sys.exit(1)
