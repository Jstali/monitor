import requests
import json

API_URL = 'http://localhost:5001/api'
EMAIL = 'stalinj4747@gmail.com'
PASSWORD = 'password123'

def check_activities():
    # Login
    res = requests.post(f'{API_URL}/auth/login', json={'email': EMAIL, 'password': PASSWORD})
    token = res.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get Sessions
    res = requests.get(f'{API_URL}/monitoring/sessions', headers=headers)
    sessions = res.json()
    
    if not sessions:
        print("No sessions found.")
        return

    latest_session = sessions[0]
    print(f"Latest Session ID: {latest_session['id']}")
    print(f"Start Time: {latest_session['start_time']}")
    
    # Get Activities
    res = requests.get(f'{API_URL}/monitoring/activities', headers=headers, params={'session_id': latest_session['id']})
    activities = res.json()
    
    print(f"Activities Found: {len(activities)}")
    for act in activities:
        print(f" - [{act['timestamp']}] {act['activity_type']}: {act['application_name']} - {act['window_title']}")

if __name__ == '__main__':
    check_activities()
