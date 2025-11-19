import requests
import sys
import os
from datetime import datetime

# Configuration
API_URL = 'http://localhost:5001/api'
EMAIL = 'stalinj4747@gmail.com'
PASSWORD = 'password123'

def log(msg, type='INFO'):
    print(f"[{type}] {msg}")

def test_system():
    session = requests.Session()
    
    # 1. Test Authentication
    log("Testing Authentication...")
    try:
        res = session.post(f'{API_URL}/auth/login', json={'email': EMAIL, 'password': PASSWORD})
        if res.status_code != 200:
            log(f"Login failed: {res.text}", 'ERROR')
            return False
        
        token = res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        log("Authentication Successful", 'SUCCESS')
    except Exception as e:
        log(f"Connection failed: {e}", 'ERROR')
        return False

    # 2. Test Start Session
    log("Testing Start Session...")
    try:
        res = requests.post(f'{API_URL}/monitoring/sessions/start', headers=headers)
        if res.status_code == 201:
            session_data = res.json().get('session')
            session_id = session_data['id']
            log(f"Session Started: ID {session_id}", 'SUCCESS')
        elif res.status_code == 400 and 'Active session already exists' in res.text:
            log("Active session already exists (Expected if not stopped)", 'INFO')
            # Get current session to continue
            res = requests.get(f'{API_URL}/monitoring/sessions/current', headers=headers)
            session_id = res.json().get('session')['id']
        else:
            log(f"Start Session failed: {res.text}", 'ERROR')
            return False
    except Exception as e:
        log(f"Start Session failed: {e}", 'ERROR')
        return False

    # 3. Test Polling (Get Current Session)
    log("Testing Polling (Get Current Session)...")
    try:
        res = requests.get(f'{API_URL}/monitoring/sessions/current', headers=headers)
        data = res.json()
        if res.status_code == 200 and data.get('session') and data['session']['is_active']:
            log(f"Polling Successful: Active Session {data['session']['id']} detected", 'SUCCESS')
        else:
            log(f"Polling failed or no active session: {res.text}", 'ERROR')
            return False
    except Exception as e:
        log(f"Polling failed: {e}", 'ERROR')
        return False

    # 4. Test Screenshot Upload
    log("Testing Screenshot Upload...")
    try:
        # Create a dummy image
        from PIL import Image
        from io import BytesIO
        
        img = Image.new('RGB', (100, 100), color = 'red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        files = {'file': ('test_screenshot.png', img_byte_arr, 'image/png')}
        
        res = requests.post(f'{API_URL}/screenshots/upload', headers=headers, files=files)
        if res.status_code == 201:
            log("Screenshot Upload Successful", 'SUCCESS')
        else:
            log(f"Screenshot Upload failed: {res.text}", 'ERROR')
            return False
    except Exception as e:
        log(f"Screenshot Upload failed: {e}", 'ERROR')
        return False

    # 5. Test Stop Session
    log("Testing Stop Session...")
    try:
        res = requests.post(f'{API_URL}/monitoring/sessions/stop', headers=headers)
        if res.status_code == 200:
            log("Session Stopped Successfully", 'SUCCESS')
        else:
            log(f"Stop Session failed: {res.text}", 'ERROR')
            return False
    except Exception as e:
        log(f"Stop Session failed: {e}", 'ERROR')
        return False

    log("ALL SYSTEMS GO! Backend is working correctly.", 'SUCCESS')
    return True

if __name__ == '__main__':
    test_system()
