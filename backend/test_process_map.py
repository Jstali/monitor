#!/usr/bin/env python3
"""Test process map endpoint"""
import requests
import sys

API_URL = "http://localhost:5001/api"
EMAIL = "stalinj4747@gmail.com"
PASSWORD = "password123"

def test_process_map():
    # Login
    print("Logging in...")
    response = requests.post(f"{API_URL}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()['access_token']
    print(f"✓ Logged in successfully")
    
    # Get active or recent session
    print("\nFetching sessions...")
    response = requests.get(
        f"{API_URL}/monitoring/sessions",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"Failed to get sessions: {response.status_code}")
        return
    
    sessions = response.json()
    if not sessions:
        print("No sessions found")
        return
    
    session_id = sessions[0]['id']
    print(f"✓ Using session ID: {session_id}")
    
    # Test JSON format
    print(f"\nTesting JSON format...")
    response = requests.get(
        f"{API_URL}/workflow/session/{session_id}/process-map?format=json",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Statistics: {data.get('statistics', {})}")
    else:
        print(f"Error: {response.text}")
    
    # Test PNG format
    print(f"\nTesting PNG format...")
    response = requests.get(
        f"{API_URL}/workflow/session/{session_id}/process-map?format=png",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        # Save to file
        with open('/tmp/process_map_test.png', 'wb') as f:
            f.write(response.content)
        print("✓ PNG saved to /tmp/process_map_test.png")
        
        # Check if it's actually a PNG
        if response.content.startswith(b'\x89PNG'):
            print("✓ Valid PNG file")
        else:
            print("✗ Not a valid PNG file!")
            print(f"First 100 bytes: {response.content[:100]}")
    else:
        print(f"Error: {response.text}")

if __name__ == '__main__':
    test_process_map()
