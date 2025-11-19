import requests
import json

API_URL = 'http://localhost:5001/api'
EMAIL = 'stalinj4747@gmail.com'
PASSWORD = 'password123'

def verify_workflow():
    print("Verifying Workflow Generation...")
    
    # 1. Login
    res = requests.post(f'{API_URL}/auth/login', json={'email': EMAIL, 'password': PASSWORD})
    token = res.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. Get Session
    res = requests.get(f'{API_URL}/monitoring/sessions', headers=headers)
    session_id = res.json()[0]['id']
    
    # 3. Generate Diagram
    print("Generating Diagram...")
    res = requests.get(f'{API_URL}/workflow/session/{session_id}/diagram', headers=headers)
    
    data = res.json()
    mermaid = data.get('mermaid_diagram', '')
    
    print("\n--- Generated Mermaid Diagram ---")
    print(mermaid[:500] + "..." if len(mermaid) > 500 else mermaid)
    print("\n---------------------------------")
    
    if "graph LR" in mermaid and "--" in mermaid and "s" in mermaid:
        print("✓ SUCCESS: Mermaid diagram generated with durations.")
    else:
        print("✗ FAILURE: Mermaid diagram missing duration labels.")

if __name__ == '__main__':
    verify_workflow()
