#!/usr/bin/env python3
"""
Comprehensive API Endpoint Test
Tests all critical endpoints to identify issues
"""
import requests
import json

API_URL = 'http://localhost:5001/api'

def test_endpoints():
    print("=" * 60)
    print("API ENDPOINT COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: Employee Login
    print("\n1. Testing Employee Login...")
    try:
        res = requests.post(f'{API_URL}/auth/login', json={
            'email': 'stalinj4747@gmail.com',
            'password': 'password123'
        })
        print(f"   Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            employee_token = data.get('access_token')
            employee_data = data.get('employee')
            print(f"   ✓ Employee login successful")
            print(f"   Employee: {employee_data['name']} ({employee_data['email']})")
        else:
            print(f"   ✗ Login failed: {res.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    headers = {'Authorization': f'Bearer {employee_token}'}
    
    # Test 2: Admin Login
    print("\n2. Testing Admin Login...")
    try:
        res = requests.post(f'{API_URL}/auth/login', json={
            'email': 'stalinstalin11112@gmail.com',
            'password': 'admin123'
        })
        print(f"   Status: {res.status_code}")
        if res.status_code == 200:
            admin_token = res.json().get('access_token')
            print(f"   ✓ Admin login successful")
        else:
            print(f"   ✗ Admin login failed: {res.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test 3: Start Session
    print("\n3. Testing Start Session...")
    try:
        res = requests.post(f'{API_URL}/monitoring/sessions/start', headers=headers)
        print(f"   Status: {res.status_code}")
        if res.status_code in [200, 201]:
            session = res.json().get('session')
            session_id = session['id']
            print(f"   ✓ Session started: ID={session_id}")
        else:
            print(f"   ✗ Failed: {res.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Get Current Session
    print("\n4. Testing Get Current Session...")
    try:
        res = requests.get(f'{API_URL}/monitoring/sessions/current', headers=headers)
        print(f"   Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"   ✓ Current session retrieved")
            print(f"   Session: {data.get('session', {}).get('id')}")
        else:
            print(f"   ✗ Failed: {res.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: Screenshot Upload
    print("\n5. Testing Screenshot Upload...")
    try:
        # Create a dummy image file
        import io
        from PIL import Image
        
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {'file': ('test.png', img_bytes, 'image/png')}
        res = requests.post(f'{API_URL}/screenshots/upload', 
                          headers={'Authorization': f'Bearer {employee_token}'},
                          files=files)
        print(f"   Status: {res.status_code}")
        if res.status_code == 200:
            screenshot_data = res.json()
            screenshot_id = screenshot_data.get('id')
            print(f"   ✓ Screenshot uploaded: ID={screenshot_id}")
        else:
            print(f"   ✗ Upload failed: {res.text}")
            screenshot_id = None
    except Exception as e:
        print(f"   ✗ Error: {e}")
        screenshot_id = None
    
    # Test 6: Get Session Screenshots (as admin)
    print("\n6. Testing Get Session Screenshots...")
    try:
        res = requests.get(f'{API_URL}/screenshots/session/{session_id}', headers=admin_headers)
        print(f"   Status: {res.status_code}")
        if res.status_code == 200:
            screenshots = res.json()
            print(f"   ✓ Retrieved {len(screenshots)} screenshots")
        else:
            print(f"   ✗ Failed: {res.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 7: Download Screenshot
    if screenshot_id:
        print("\n7. Testing Download Screenshot...")
        try:
            res = requests.get(f'{API_URL}/screenshots/{screenshot_id}/file', headers=admin_headers)
            print(f"   Status: {res.status_code}")
            if res.status_code == 200:
                print(f"   ✓ Screenshot downloaded ({len(res.content)} bytes)")
            else:
                print(f"   ✗ Download failed: {res.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Test 8: Extract Screenshot Data
    if screenshot_id:
        print("\n8. Testing Extract Screenshot Data...")
        try:
            res = requests.post(f'{API_URL}/screenshots/{screenshot_id}/extract', headers=headers)
            print(f"   Status: {res.status_code}")
            if res.status_code == 200:
                print(f"   ✓ Extraction successful")
                data = res.json()
                print(f"   Extracted: {data.get('screenshot', {}).get('extracted_text', '')[:50]}...")
            else:
                print(f"   ✗ Extraction failed: {res.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Test 9: Stop Session
    print("\n9. Testing Stop Session...")
    try:
        res = requests.post(f'{API_URL}/monitoring/sessions/stop', headers=headers)
        print(f"   Status: {res.status_code}")
        if res.status_code == 200:
            print(f"   ✓ Session stopped successfully")
        else:
            print(f"   ✗ Failed: {res.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        test_endpoints()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
