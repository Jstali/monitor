#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all endpoints of the Employee Monitoring Application
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import os
from pathlib import Path

# Configuration
BASE_URL = os.getenv('API_URL', 'http://localhost:3535/api')
TEST_EMAIL = f"test_user_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_ORG_NAME = f"Test Organization {int(time.time())}"
ADMIN_EMAIL = f"test_admin_{int(time.time())}@example.com"
ADMIN_PASSWORD = "AdminPassword123!"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'errors': []
}

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def print_test(test_name: str, status: str, message: str = ""):
    """Print test result"""
    if status == "PASS":
        color = Colors.GREEN
        symbol = "✓"
        test_results['passed'] += 1
    elif status == "FAIL":
        color = Colors.RED
        symbol = "✗"
        test_results['failed'] += 1
        test_results['errors'].append(f"{test_name}: {message}")
    elif status == "SKIP":
        color = Colors.YELLOW
        symbol = "⊘"
        test_results['skipped'] += 1
    else:
        color = Colors.BLUE
        symbol = "→"
    
    print(f"{color}{symbol} {test_name}{Colors.RESET}")
    if message:
        print(f"  {Colors.YELLOW}{message}{Colors.RESET}")

def make_request(method: str, endpoint: str, token: str = None, data: dict = None, 
                files: dict = None, params: dict = None) -> Tuple[int, dict]:
    """Make HTTP request and return status code and response"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    if data and not files:
        headers['Content-Type'] = 'application/json'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return 0, {'error': 'Invalid method'}
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {'raw': response.text}
    except requests.exceptions.RequestException as e:
        return 0, {'error': str(e)}

def test_health_check():
    """Test health check endpoint"""
    print_header("HEALTH CHECK")
    
    status, response = make_request('GET', '/health')
    
    if status == 200 and response.get('status') == 'healthy':
        print_test("GET /api/health", "PASS", "Server is healthy")
        return True
    else:
        print_test("GET /api/health", "FAIL", f"Status: {status}, Response: {response}")
        return False

def test_authentication() -> Tuple[str, str]:
    """Test authentication endpoints"""
    print_header("AUTHENTICATION ENDPOINTS")
    
    # Test registration - Employee
    print(f"\n{Colors.BOLD}Testing Employee Registration{Colors.RESET}")
    status, response = make_request('POST', '/auth/register', data={
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'name': 'Test Employee',
        'organization_name': TEST_ORG_NAME,
        'role': 'employee'
    })
    
    if status == 201:
        print_test("POST /api/auth/register (employee)", "PASS")
    else:
        print_test("POST /api/auth/register (employee)", "FAIL", f"Status: {status}, Response: {response}")
    
    # Test registration - Admin
    print(f"\n{Colors.BOLD}Testing Admin Registration{Colors.RESET}")
    status, response = make_request('POST', '/auth/register', data={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD,
        'name': 'Test Admin',
        'organization_name': TEST_ORG_NAME,
        'role': 'admin'
    })
    
    if status == 201:
        print_test("POST /api/auth/register (admin)", "PASS")
    else:
        print_test("POST /api/auth/register (admin)", "FAIL", f"Status: {status}, Response: {response}")
    
    # Test duplicate registration
    status, response = make_request('POST', '/auth/register', data={
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'name': 'Duplicate User',
        'organization_name': TEST_ORG_NAME,
        'role': 'employee'
    })
    
    if status == 400:
        print_test("POST /api/auth/register (duplicate)", "PASS", "Correctly rejected duplicate email")
    else:
        print_test("POST /api/auth/register (duplicate)", "FAIL", "Should reject duplicate email")
    
    # Test login - Employee
    print(f"\n{Colors.BOLD}Testing Employee Login{Colors.RESET}")
    status, response = make_request('POST', '/auth/login', data={
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    })
    
    employee_token = None
    if status == 200 and 'access_token' in response:
        employee_token = response['access_token']
        print_test("POST /api/auth/login (employee)", "PASS")
    else:
        print_test("POST /api/auth/login (employee)", "FAIL", f"Status: {status}, Response: {response}")
    
    # Test login - Admin
    print(f"\n{Colors.BOLD}Testing Admin Login{Colors.RESET}")
    status, response = make_request('POST', '/auth/login', data={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    
    admin_token = None
    if status == 200 and 'access_token' in response:
        admin_token = response['access_token']
        print_test("POST /api/auth/login (admin)", "PASS")
    else:
        print_test("POST /api/auth/login (admin)", "FAIL", f"Status: {status}, Response: {response}")
    
    # Test invalid login
    status, response = make_request('POST', '/auth/login', data={
        'email': TEST_EMAIL,
        'password': 'WrongPassword'
    })
    
    if status == 401:
        print_test("POST /api/auth/login (invalid)", "PASS", "Correctly rejected invalid credentials")
    else:
        print_test("POST /api/auth/login (invalid)", "FAIL", "Should reject invalid credentials")
    
    # Test get current user
    if employee_token:
        status, response = make_request('GET', '/auth/me', token=employee_token)
        if status == 200 and 'email' in response:
            print_test("GET /api/auth/me", "PASS")
        else:
            print_test("GET /api/auth/me", "FAIL", f"Status: {status}")
    
    return employee_token, admin_token

def test_monitoring_endpoints(token: str):
    """Test monitoring endpoints"""
    print_header("MONITORING ENDPOINTS")
    
    session_id = None
    
    # Start session
    print(f"\n{Colors.BOLD}Testing Session Management{Colors.RESET}")
    status, response = make_request('POST', '/monitoring/sessions/start', token=token, data={
        'agent_email': 'agent@example.com',
        'agent_password': 'AgentPassword123'
    })
    
    if status == 201 and 'session' in response:
        session_id = response['session']['id']
        print_test("POST /api/monitoring/sessions/start", "PASS", f"Session ID: {session_id}")
    else:
        print_test("POST /api/monitoring/sessions/start", "FAIL", f"Status: {status}, Response: {response}")
    
    # Get current session
    status, response = make_request('GET', '/monitoring/sessions/current', token=token)
    if status == 200:
        print_test("GET /api/monitoring/sessions/current", "PASS")
    else:
        print_test("GET /api/monitoring/sessions/current", "FAIL", f"Status: {status}")
    
    # Get sessions list
    status, response = make_request('GET', '/monitoring/sessions', token=token)
    if status == 200:
        print_test("GET /api/monitoring/sessions", "PASS", f"Found {len(response)} sessions")
    else:
        print_test("GET /api/monitoring/sessions", "FAIL", f"Status: {status}")
    
    # Log activity
    print(f"\n{Colors.BOLD}Testing Activity Logging{Colors.RESET}")
    status, response = make_request('POST', '/monitoring/activities', token=token, data={
        'activity_type': 'application',
        'application_name': 'Google Chrome',
        'window_title': 'Test Window',
        'duration_seconds': 60
    })
    
    if status == 201:
        print_test("POST /api/monitoring/activities (application)", "PASS")
    else:
        print_test("POST /api/monitoring/activities (application)", "FAIL", f"Status: {status}")
    
    # Log website activity
    status, response = make_request('POST', '/monitoring/activities', token=token, data={
        'activity_type': 'website',
        'application_name': 'Google Chrome',
        'url': 'https://example.com',
        'duration_seconds': 30
    })
    
    if status == 201:
        print_test("POST /api/monitoring/activities (website)", "PASS")
    else:
        print_test("POST /api/monitoring/activities (website)", "FAIL", f"Status: {status}")
    
    # Get activities
    if session_id:
        status, response = make_request('GET', '/monitoring/activities', token=token, 
                                       params={'session_id': session_id})
        if status == 200:
            print_test("GET /api/monitoring/activities", "PASS", f"Found {len(response)} activities")
        else:
            print_test("GET /api/monitoring/activities", "FAIL", f"Status: {status}")
    
    # Test agent credentials
    print(f"\n{Colors.BOLD}Testing Agent Credentials{Colors.RESET}")
    
    # Get credentials status
    status, response = make_request('GET', '/monitoring/agent/credentials/status', token=token)
    if status == 200:
        print_test("GET /api/monitoring/agent/credentials/status", "PASS", 
                  f"Has credentials: {response.get('has_credentials')}")
    else:
        print_test("GET /api/monitoring/agent/credentials/status", "FAIL", f"Status: {status}")
    
    # Update credentials
    status, response = make_request('PUT', '/monitoring/agent/credentials', token=token, data={
        'agent_email': 'updated@example.com',
        'agent_password': 'UpdatedPassword123'
    })
    
    if status == 200:
        print_test("PUT /api/monitoring/agent/credentials", "PASS")
    else:
        print_test("PUT /api/monitoring/agent/credentials", "FAIL", f"Status: {status}")
    
    # Get credentials
    status, response = make_request('GET', '/monitoring/agent/credentials', token=token)
    if status == 200 and 'email' in response:
        print_test("GET /api/monitoring/agent/credentials", "PASS")
    else:
        print_test("GET /api/monitoring/agent/credentials", "FAIL", f"Status: {status}")
    
    # Stop session
    time.sleep(1)  # Ensure session has some duration
    status, response = make_request('POST', '/monitoring/sessions/stop', token=token)
    if status == 200:
        print_test("POST /api/monitoring/sessions/stop", "PASS")
    else:
        print_test("POST /api/monitoring/sessions/stop", "FAIL", f"Status: {status}")
    
    return session_id

def test_screenshot_endpoints(token: str, session_id: int):
    """Test screenshot endpoints"""
    print_header("SCREENSHOT ENDPOINTS")
    
    # Create a test image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Upload screenshot
    print(f"\n{Colors.BOLD}Testing Screenshot Upload{Colors.RESET}")
    
    # First, start a new session for screenshot upload
    status, response = make_request('POST', '/monitoring/sessions/start', token=token)
    if status != 201:
        print_test("Screenshot upload", "SKIP", "Could not start session for upload")
        return None
    
    files = {'file': ('test_screenshot.png', img_bytes, 'image/png')}
    data = {
        'folder_name': 'test_folder',
        'activity_name': 'Test Activity'
    }
    
    status, response = make_request('POST', '/screenshots/upload', token=token, 
                                   data=data, files=files)
    
    screenshot_id = None
    if status == 201 and 'screenshot' in response:
        screenshot_id = response['screenshot']['id']
        print_test("POST /api/screenshots/upload", "PASS", f"Screenshot ID: {screenshot_id}")
    else:
        print_test("POST /api/screenshots/upload", "FAIL", f"Status: {status}, Response: {response}")
    
    if screenshot_id:
        # Get screenshot details
        status, response = make_request('GET', f'/screenshots/{screenshot_id}', token=token)
        if status == 200:
            print_test("GET /api/screenshots/:id", "PASS")
        else:
            print_test("GET /api/screenshots/:id", "FAIL", f"Status: {status}")
        
        # Extract screenshot data
        print(f"\n{Colors.BOLD}Testing Screenshot Extraction{Colors.RESET}")
        status, response = make_request('POST', f'/screenshots/{screenshot_id}/extract', token=token)
        if status == 200:
            print_test("POST /api/screenshots/:id/extract", "PASS")
        else:
            print_test("POST /api/screenshots/:id/extract", "FAIL", f"Status: {status}")
    
    # Get session screenshots
    if session_id:
        status, response = make_request('GET', f'/screenshots/session/{session_id}', token=token)
        if status == 200:
            print_test("GET /api/screenshots/session/:id", "PASS", f"Found {len(response)} screenshots")
        else:
            print_test("GET /api/screenshots/session/:id", "FAIL", f"Status: {status}")
    
    # Stop the session
    make_request('POST', '/monitoring/sessions/stop', token=token)
    
    return screenshot_id

def test_employee_endpoints(employee_token: str, admin_token: str):
    """Test employee endpoints"""
    print_header("EMPLOYEE ENDPOINTS")
    
    # Get own profile
    print(f"\n{Colors.BOLD}Testing Employee Profile{Colors.RESET}")
    status, response = make_request('GET', '/employees/me', token=employee_token)
    
    employee_id = None
    if status == 200 and 'id' in response:
        employee_id = response['id']
        print_test("GET /api/employees/me", "PASS", f"Employee ID: {employee_id}")
    else:
        print_test("GET /api/employees/me", "FAIL", f"Status: {status}")
    
    # Update own profile
    status, response = make_request('PUT', '/employees/me', token=employee_token, data={
        'name': 'Updated Test Employee'
    })
    
    if status == 200:
        print_test("PUT /api/employees/me", "PASS")
    else:
        print_test("PUT /api/employees/me", "FAIL", f"Status: {status}")
    
    # Admin get employee
    if employee_id and admin_token:
        print(f"\n{Colors.BOLD}Testing Admin Employee Access{Colors.RESET}")
        status, response = make_request('GET', f'/employees/{employee_id}', token=admin_token)
        if status == 200:
            print_test("GET /api/employees/:id (admin)", "PASS")
        else:
            print_test("GET /api/employees/:id (admin)", "FAIL", f"Status: {status}")
        
        # Admin update employee
        status, response = make_request('PUT', f'/employees/{employee_id}', token=admin_token, data={
            'is_active': True
        })
        if status == 200:
            print_test("PUT /api/employees/:id (admin)", "PASS")
        else:
            print_test("PUT /api/employees/:id (admin)", "FAIL", f"Status: {status}")
    
    return employee_id

def test_organization_endpoints(admin_token: str):
    """Test organization endpoints"""
    print_header("ORGANIZATION ENDPOINTS")
    
    # Get own organization
    status, response = make_request('GET', '/employees/me', token=admin_token)
    
    org_id = None
    if status == 200 and 'organization_id' in response:
        org_id = response['organization_id']
    
    if org_id:
        # Get organization details
        status, response = make_request('GET', f'/organizations/{org_id}', token=admin_token)
        if status == 200:
            print_test("GET /api/organizations/:id", "PASS")
        else:
            print_test("GET /api/organizations/:id", "FAIL", f"Status: {status}")
        
        # Update organization
        status, response = make_request('PUT', f'/organizations/{org_id}', token=admin_token, data={
            'screenshot_interval': 30
        })
        if status == 200:
            print_test("PUT /api/organizations/:id", "PASS")
        else:
            print_test("PUT /api/organizations/:id", "FAIL", f"Status: {status}")
        
        # Get organization employees
        status, response = make_request('GET', f'/organizations/{org_id}/employees', token=admin_token)
        if status == 200:
            print_test("GET /api/organizations/:id/employees", "PASS", f"Found {len(response)} employees")
        else:
            print_test("GET /api/organizations/:id/employees", "FAIL", f"Status: {status}")
    
    return org_id

def test_monitoring_config_endpoints(admin_token: str):
    """Test monitoring configuration endpoints"""
    print_header("MONITORING CONFIGURATION ENDPOINTS")
    
    # Get all configs
    status, response = make_request('GET', '/monitoring-config/', token=admin_token)
    if status == 200:
        print_test("GET /api/monitoring-config/", "PASS", f"Found {len(response)} configs")
    else:
        print_test("GET /api/monitoring-config/", "FAIL", f"Status: {status}")
    
    # Create config
    print(f"\n{Colors.BOLD}Testing Config Creation{Colors.RESET}")
    status, response = make_request('POST', '/monitoring-config/', token=admin_token, data={
        'config_type': 'application',
        'pattern': 'Chrome',
        'folder_name': 'chrome_activity',
        'is_active': True
    })
    
    config_id = None
    if status == 201 and 'config' in response:
        config_id = response['config']['id']
        print_test("POST /api/monitoring-config/ (application)", "PASS", f"Config ID: {config_id}")
    else:
        print_test("POST /api/monitoring-config/ (application)", "FAIL", f"Status: {status}")
    
    # Create URL config
    status, response = make_request('POST', '/monitoring-config/', token=admin_token, data={
        'config_type': 'url',
        'pattern': 'github.com',
        'folder_name': 'github_activity',
        'is_active': True
    })
    
    if status == 201:
        print_test("POST /api/monitoring-config/ (url)", "PASS")
    else:
        print_test("POST /api/monitoring-config/ (url)", "FAIL", f"Status: {status}")
    
    # Get active configs
    status, response = make_request('GET', '/monitoring-config/active', token=admin_token)
    if status == 200:
        print_test("GET /api/monitoring-config/active", "PASS", f"Found {len(response)} active configs")
    else:
        print_test("GET /api/monitoring-config/active", "FAIL", f"Status: {status}")
    
    if config_id:
        # Update config
        status, response = make_request('PUT', f'/monitoring-config/{config_id}', token=admin_token, data={
            'pattern': 'Google Chrome',
            'is_active': False
        })
        if status == 200:
            print_test("PUT /api/monitoring-config/:id", "PASS")
        else:
            print_test("PUT /api/monitoring-config/:id", "FAIL", f"Status: {status}")
        
        # Delete config
        status, response = make_request('DELETE', f'/monitoring-config/{config_id}', token=admin_token)
        if status == 200:
            print_test("DELETE /api/monitoring-config/:id", "PASS")
        else:
            print_test("DELETE /api/monitoring-config/:id", "FAIL", f"Status: {status}")

def test_workflow_endpoints(token: str, session_id: int):
    """Test workflow endpoints"""
    print_header("WORKFLOW ENDPOINTS")
    
    if not session_id:
        print_test("Workflow tests", "SKIP", "No session ID available")
        return
    
    # Generate process map (JSON)
    status, response = make_request('GET', f'/workflow/session/{session_id}/process-map', 
                                   token=token, params={'format': 'json'})
    if status == 200:
        print_test("GET /api/workflow/session/:id/process-map (json)", "PASS")
    else:
        print_test("GET /api/workflow/session/:id/process-map (json)", "FAIL", f"Status: {status}")
    
    # Generate workflow diagram (JSON)
    status, response = make_request('GET', f'/workflow/session/{session_id}/diagram', 
                                   token=token, params={'format': 'json'})
    if status == 200:
        print_test("GET /api/workflow/session/:id/diagram (json)", "PASS")
    else:
        print_test("GET /api/workflow/session/:id/diagram (json)", "FAIL", f"Status: {status}")

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = test_results['passed'] + test_results['failed'] + test_results['skipped']
    
    print(f"{Colors.BOLD}Total Tests:{Colors.RESET} {total}")
    print(f"{Colors.GREEN}✓ Passed:{Colors.RESET} {test_results['passed']}")
    print(f"{Colors.RED}✗ Failed:{Colors.RESET} {test_results['failed']}")
    print(f"{Colors.YELLOW}⊘ Skipped:{Colors.RESET} {test_results['skipped']}")
    
    if test_results['passed'] > 0:
        success_rate = (test_results['passed'] / total) * 100
        print(f"\n{Colors.BOLD}Success Rate:{Colors.RESET} {success_rate:.1f}%")
    
    if test_results['errors']:
        print(f"\n{Colors.RED}{Colors.BOLD}ERRORS FOUND:{Colors.RESET}")
        for error in test_results['errors']:
            print(f"{Colors.RED}  • {error}{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def main():
    """Main test execution"""
    print_header("COMPREHENSIVE API TESTING")
    print(f"{Colors.BOLD}Base URL:{Colors.RESET} {BASE_URL}")
    print(f"{Colors.BOLD}Start Time:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    if not test_health_check():
        print(f"\n{Colors.RED}{Colors.BOLD}ERROR: Server is not running or not healthy!{Colors.RESET}")
        print(f"{Colors.YELLOW}Please start the backend server first:{Colors.RESET}")
        print(f"  cd backend && python app.py")
        return
    
    # Run tests
    employee_token, admin_token = test_authentication()
    
    if not employee_token or not admin_token:
        print(f"\n{Colors.RED}{Colors.BOLD}ERROR: Authentication failed!{Colors.RESET}")
        print_summary()
        return
    
    session_id = test_monitoring_endpoints(employee_token)
    screenshot_id = test_screenshot_endpoints(employee_token, session_id)
    employee_id = test_employee_endpoints(employee_token, admin_token)
    org_id = test_organization_endpoints(admin_token)
    test_monitoring_config_endpoints(admin_token)
    test_workflow_endpoints(employee_token, session_id)
    
    # Print summary
    print_summary()
    
    print(f"{Colors.BOLD}End Time:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test execution interrupted by user{Colors.RESET}")
        print_summary()
    except Exception as e:
        print(f"\n\n{Colors.RED}{Colors.BOLD}FATAL ERROR:{Colors.RESET} {str(e)}")
        import traceback
        traceback.print_exc()
        print_summary()
