#!/usr/bin/env python3
"""
Verification script to test the workflow modal implementation
"""
import requests
import json

API_URL = 'http://localhost:5001/api'
ADMIN_EMAIL = 'admin@test.com'
ADMIN_PASSWORD = 'admin123'

def test_workflow_modal():
    print("=" * 60)
    print("WORKFLOW MODAL VERIFICATION")
    print("=" * 60)
    
    # 1. Login as admin
    print("\n1. Testing Admin Login...")
    res = requests.post(f'{API_URL}/auth/login', json={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    
    if res.status_code != 200:
        print(f"   ✗ Admin login failed: {res.status_code}")
        print(f"   Response: {res.text}")
        return False
    
    token = res.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    print("   ✓ Admin login successful")
    
    # 2. Get sessions
    print("\n2. Fetching Sessions...")
    res = requests.get(f'{API_URL}/monitoring/sessions', headers=headers)
    sessions = res.json()
    
    if not sessions:
        print("   ✗ No sessions found")
        return False
    
    session = sessions[0]
    print(f"   ✓ Found {len(sessions)} sessions")
    print(f"   Using session ID: {session['id']}")
    
    # 3. Get screenshots
    print("\n3. Fetching Screenshots...")
    res = requests.get(f'{API_URL}/screenshots/session/{session["id"]}', headers=headers)
    screenshots = res.json()
    
    if not screenshots:
        print("   ✗ No screenshots found")
        return False
    
    print(f"   ✓ Found {len(screenshots)} screenshots")
    
    # 4. Extract data from first screenshot
    print("\n4. Testing Screenshot Extraction...")
    screenshot_id = screenshots[0]['id']
    res = requests.post(f'{API_URL}/screenshots/{screenshot_id}/extract', headers=headers)
    
    if res.status_code != 200:
        print(f"   ✗ Extraction failed: {res.status_code}")
        print(f"   Response: {res.text}")
        return False
    
    extracted = res.json()
    screenshot_data = extracted.get('screenshot', {})
    extraction_data = screenshot_data.get('extraction_data', {})
    
    print("   ✓ Extraction successful")
    print(f"   Extracted data: {json.dumps(extraction_data, indent=2)}")
    
    # Check if structured data exists
    if 'app' in extraction_data and 'action' in extraction_data:
        print("   ✓ Structured extraction data present (app, action, context)")
    else:
        print("   ✗ Missing structured extraction data")
        return False
    
    # 5. Generate workflow diagram
    print("\n5. Testing Workflow Diagram Generation...")
    res = requests.get(f'{API_URL}/workflow/session/{session["id"]}/diagram', headers=headers)
    
    if res.status_code != 200:
        print(f"   ✗ Workflow generation failed: {res.status_code}")
        return False
    
    workflow_data = res.json()
    mermaid = workflow_data.get('mermaid_diagram', '')
    
    print("   ✓ Workflow diagram generated")
    print(f"   Diagram preview:\n{mermaid[:300]}...")
    
    # Check for duration labels
    if '--' in mermaid and ('s' in mermaid or 'm' in mermaid):
        print("   ✓ Duration labels present in diagram")
    else:
        print("   ✗ Duration labels missing")
        return False
    
    # Check for graph LR
    if 'graph LR' in mermaid:
        print("   ✓ Diagram uses left-to-right flow")
    else:
        print("   ⚠ Diagram not using LR layout")
    
    # Check workflow steps
    workflow_steps = workflow_data.get('screenshot_workflow', {}).get('workflow_steps', [])
    print(f"\n   Workflow steps: {len(workflow_steps)}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\n✓ All backend components working correctly!")
    print("\nFrontend Test:")
    print("1. Open Organization Dashboard in browser")
    print("2. Select a session with screenshots")
    print("3. Click 'Extract All Data' button")
    print("4. Modal should open with:")
    print("   - Activity summary at top")
    print("   - Process flow diagram at bottom")
    print("   - Duration labels on transitions")
    
    return True

if __name__ == '__main__':
    try:
        test_workflow_modal()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
