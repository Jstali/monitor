import requests
import json

API_URL = 'http://localhost:5001/api'
EMAIL = 'stalinj4747@gmail.com'
PASSWORD = 'password123'

def verify_extraction():
    print("Verifying Extraction Endpoint...")
    
    # 1. Login
    try:
        res = requests.post(f'{API_URL}/auth/login', json={'email': EMAIL, 'password': PASSWORD})
        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            return
        token = res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        print("✓ Login successful")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 2. Get Latest Session
    try:
        res = requests.get(f'{API_URL}/monitoring/sessions', headers=headers)
        sessions = res.json()
        if not sessions:
            print("No sessions found")
            return
        
        latest_session = sessions[0]
        print(f"✓ Found session {latest_session['id']}")
    except Exception as e:
        print(f"Failed to get sessions: {e}")
        return

    # 3. Get Screenshots for Session
    try:
        res = requests.get(f'{API_URL}/screenshots/session/{latest_session["id"]}', headers=headers)
        screenshots = res.json()
        if not screenshots:
            print("No screenshots in this session")
            return
        
        target_screenshot = screenshots[0]
        print(f"✓ Found screenshot {target_screenshot['id']} (Processed: {target_screenshot.get('is_processed')})")
    except Exception as e:
        print(f"Failed to get screenshots: {e}")
        return

    # 4. Trigger Extraction
    print(f"Triggering extraction for screenshot {target_screenshot['id']}...")
    try:
        res = requests.post(f'{API_URL}/screenshots/{target_screenshot["id"]}/extract', headers=headers)
        
        print(f"Response Status: {res.status_code}")
        print(f"Response Body: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 200:
            print("✓ Extraction successful")
        else:
            print("✗ Extraction failed")
            
    except Exception as e:
        print(f"Extraction call failed: {e}")

if __name__ == '__main__':
    verify_extraction()
