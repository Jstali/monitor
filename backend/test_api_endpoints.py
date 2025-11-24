#!/usr/bin/env python3
"""
API Endpoint Testing Script
Tests all endpoints to ensure they're working correctly
"""

import requests
import json

API_URL = "http://localhost:5001/api"

# Test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_endpoint(method, endpoint, description, requires_auth=False, token=None):
    """Test a single endpoint"""
    url = f"{API_URL}{endpoint}"
    headers = {}
    
    if requires_auth and token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, timeout=5)
        elif method == "OPTIONS":
            response = requests.options(url, timeout=5)
        
        status = response.status_code
        
        # Check if endpoint is accessible
        if method == "OPTIONS":
            if status == 200:
                results["passed"].append(f"✓ {method} {endpoint} - {description} (CORS OK)")
            else:
                results["failed"].append(f"✗ {method} {endpoint} - {description} (Status: {status})")
        elif requires_auth and status == 401:
            results["passed"].append(f"✓ {method} {endpoint} - {description} (Auth required ✓)")
        elif status in [200, 201]:
            results["passed"].append(f"✓ {method} {endpoint} - {description} (Status: {status})")
        elif status == 400:
            results["warnings"].append(f"⚠ {method} {endpoint} - {description} (Bad request - endpoint exists)")
        else:
            results["failed"].append(f"✗ {method} {endpoint} - {description} (Status: {status})")
            
    except requests.exceptions.ConnectionError:
        results["failed"].append(f"✗ {method} {endpoint} - {description} (Connection failed)")
    except Exception as e:
        results["failed"].append(f"✗ {method} {endpoint} - {description} (Error: {str(e)})")

print("=" * 70)
print("API ENDPOINT TESTING")
print("=" * 70)
print()

# Test health check
print("Testing basic endpoints...")
test_endpoint("GET", "/health", "Health check")

# Test CORS for all main endpoints
print("\nTesting CORS (OPTIONS requests)...")
test_endpoint("OPTIONS", "/auth/login", "Auth CORS")
test_endpoint("OPTIONS", "/monitoring-config", "Monitoring Config CORS")
test_endpoint("OPTIONS", "/screenshots/upload", "Screenshot Upload CORS")
test_endpoint("OPTIONS", "/workflow/session/1/process-map", "Process Map CORS")

# Test auth endpoints
print("\nTesting authentication endpoints...")
test_endpoint("POST", "/auth/login", "Login endpoint (no credentials)", requires_auth=False)
test_endpoint("GET", "/auth/me", "Get current user", requires_auth=True)

# Test monitoring config endpoints
print("\nTesting monitoring configuration endpoints...")
test_endpoint("GET", "/monitoring-config", "Get all configs", requires_auth=True)
test_endpoint("GET", "/monitoring-config/active", "Get active configs", requires_auth=True)
test_endpoint("POST", "/monitoring-config", "Create config", requires_auth=True)

# Test screenshot endpoints
print("\nTesting screenshot endpoints...")
test_endpoint("POST", "/screenshots/upload", "Upload screenshot", requires_auth=True)
test_endpoint("GET", "/screenshots/1", "Get screenshot", requires_auth=True)

# Test monitoring endpoints
print("\nTesting monitoring session endpoints...")
test_endpoint("POST", "/monitoring/sessions/start", "Start session", requires_auth=True)
test_endpoint("GET", "/monitoring/sessions/current", "Get current session", requires_auth=True)
test_endpoint("GET", "/monitoring/sessions", "Get all sessions", requires_auth=True)

# Test workflow endpoints
print("\nTesting workflow endpoints...")
test_endpoint("GET", "/workflow/session/1/diagram", "Get session diagram", requires_auth=True)
test_endpoint("GET", "/workflow/session/1/process-map", "Get process map", requires_auth=True)

# Test organization endpoints
print("\nTesting organization endpoints...")
test_endpoint("GET", "/organizations/1", "Get organization", requires_auth=True)
test_endpoint("GET", "/organizations/1/employees", "Get employees", requires_auth=True)

# Test employee endpoints
print("\nTesting employee endpoints...")
test_endpoint("GET", "/employees/me", "Get my profile", requires_auth=True)

# Print results
print("\n" + "=" * 70)
print("TEST RESULTS")
print("=" * 70)

print(f"\n✓ PASSED ({len(results['passed'])} tests):")
for result in results["passed"]:
    print(f"  {result}")

if results["warnings"]:
    print(f"\n⚠ WARNINGS ({len(results['warnings'])} tests):")
    for result in results["warnings"]:
        print(f"  {result}")

if results["failed"]:
    print(f"\n✗ FAILED ({len(results['failed'])} tests):")
    for result in results["failed"]:
        print(f"  {result}")
else:
    print("\n🎉 All critical tests passed!")

# Summary
total = len(results["passed"]) + len(results["warnings"]) + len(results["failed"])
print(f"\nSummary: {len(results['passed'])}/{total} passed, {len(results['warnings'])} warnings, {len(results['failed'])} failed")
