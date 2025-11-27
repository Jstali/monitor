#!/usr/bin/env python3
"""
Automatically refresh JWT token for monitoring agent
"""
import requests
import os
from dotenv import load_dotenv, set_key

load_dotenv()

API_URL = os.getenv('API_URL', 'http://localhost:3535/api')

print("="*70)
print("JWT Token Refresh for Monitoring Agent")
print("="*70)
print()

# Try actual user credentials from database
test_credentials = [
    ('stalinj4747@gmail.com', 'test@123'),  # Employee
    ('jstalin826@gmail.com', 'test@123'),   # Super Admin
    ('strawhatluff124@gmail.com', 'test@123'),  # Admin
]

print("🔍 Attempting to generate fresh token...")
print(f"   API URL: {API_URL}")
print()

token = None
used_email = None

for email, password in test_credentials:
    try:
        print(f"   Trying: {email}...", end=" ")
        response = requests.post(
            f"{API_URL}/auth/login",
            json={'email': email, 'password': password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            used_email = email
            print("✅ Success!")
            break
        else:
            print(f"❌ Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Error: {e}")

if token:
    print()
    print("="*70)
    print("✅ TOKEN GENERATED SUCCESSFULLY")
    print("="*70)
    print()
    print(f"Email: {used_email}")
    print(f"Token: {token[:50]}...")
    print()
    
    # Update .env file
    env_file = '.env'
    set_key(env_file, 'JWT_TOKEN', token)
    
    print("✅ Updated .env file with new token")
    print()
    print("="*70)
    print("You can now run the monitoring agent:")
    print("   python monitor_agent.py")
    print("="*70)
else:
    print()
    print("="*70)
    print("❌ COULD NOT GENERATE TOKEN")
    print("="*70)
    print()
    print("Please create a user account first:")
    print("   cd ../backend")
    print("   python3 create_super_admin.py")
    print()
    print("Or use the Employee Dashboard to register.")
    print("="*70)
