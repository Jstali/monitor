import requests
import json

API_URL = "http://localhost:5001/api"
EMAIL = "stalinj4747@gmail.com"  # Using the email from the dashboard screenshot
PASSWORD = "password123"  # Found in reset_password.py

def test_stop_session():
    print(f"Testing stop session for {EMAIL}...")
    
    # 1. Login
    try:
        login_response = requests.post(f"{API_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return
            
        token = login_response.json().get('access_token')
        print("Login successful. Token received.")
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"Login error: {e}")
        return

    # 2. Check current session
    try:
        current_response = requests.get(f"{API_URL}/monitoring/sessions/current", headers=headers)
        current_session = current_response.json().get('session')
        
        if current_session:
            print(f"Found active session ID: {current_session['id']}")
        else:
            print("No active session found. Starting one...")
            start_response = requests.post(f"{API_URL}/monitoring/sessions/start", headers=headers)
            if start_response.status_code == 201:
                print("Session started successfully.")
            else:
                print(f"Failed to start session: {start_response.status_code} - {start_response.text}")
                return
    except Exception as e:
        print(f"Check session error: {e}")
        return

    # 3. Stop session
    try:
        print("Attempting to stop session...")
        stop_response = requests.post(f"{API_URL}/monitoring/sessions/stop", headers=headers)
        
        if stop_response.status_code == 200:
            print("Session stopped successfully!")
            print(stop_response.json())
        else:
            print(f"Failed to stop session: {stop_response.status_code}")
            print(stop_response.text)
            
    except Exception as e:
        print(f"Stop session error: {e}")

if __name__ == "__main__":
    test_stop_session()
