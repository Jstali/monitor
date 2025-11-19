import requests
import json

API_URL = 'http://localhost:5001/api'
EMAIL = 'stalinj4747@gmail.com'
PASSWORD = 'password123'

def check_status():
    # Login
    res = requests.post(f'{API_URL}/auth/login', json={'email': EMAIL, 'password': PASSWORD})
    token = res.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get Sessions
    res = requests.get(f'{API_URL}/monitoring/sessions', headers=headers)
    sessions = res.json()
    if not sessions:
        print("No sessions found")
        return

    latest_session = sessions[0]
    print(f"Checking Session {latest_session['id']}")
    
    # Get Screenshots
    res = requests.get(f'{API_URL}/screenshots/session/{latest_session["id"]}', headers=headers)
    screenshots = res.json()
    
    processed_count = sum(1 for s in screenshots if s['is_processed'])
    total_count = len(screenshots)
    
    print(f"Total Screenshots: {total_count}")
    print(f"Processed: {processed_count}")
    print(f"Unprocessed: {total_count - processed_count}")
    
    if processed_count > 0:
        print("Sample Extracted Text:")
        processed = next(s for s in screenshots if s['is_processed'])
        print(processed.get('extracted_text', 'No text'))

if __name__ == '__main__':
    check_status()
