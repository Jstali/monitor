import requests
import time

API_URL = 'http://localhost:5001/api'
EMAIL = 'stalinj4747@gmail.com'
PASSWORD = 'password123'

def run():
    # Login
    res = requests.post(f'{API_URL}/auth/login', json={'email': EMAIL, 'password': PASSWORD})
    token = res.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Start Session
    print("Triggering Session Start...")
    requests.post(f'{API_URL}/monitoring/sessions/start', headers=headers)
    
    print("Waiting 20 seconds for agent to capture...")
    time.sleep(20)
    
    # Stop Session
    print("Triggering Session Stop...")
    requests.post(f'{API_URL}/monitoring/sessions/stop', headers=headers)
    print("Done.")

if __name__ == '__main__':
    run()
