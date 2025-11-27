#!/usr/bin/env python3
"""
Get JWT Token Helper
Run this to get your JWT token for the monitoring agent
"""

import requests
import sys

def get_token():
    print("=" * 60)
    print("JWT Token Generator for Monitoring Agent")
    print("=" * 60)
    
    api_url = input("\nAPI URL (press Enter for http://localhost:3535/api): ").strip()
    if not api_url:
        api_url = "http://localhost:3535/api"
    
    email = input("Your Email: ").strip()
    password = input("Your Password: ").strip()
    
    if not email or not password:
        print("\n✗ Email and password are required!")
        return
    
    try:
        print("\nAuthenticating...")
        response = requests.post(
            f'{api_url}/auth/login',
            json={'email': email, 'password': password},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        token = data['access_token']
        name = data['employee']['name']
        
        print(f"\n✓ Success! Logged in as {name}")
        print("\n" + "=" * 60)
        print("Your JWT Token:")
        print("=" * 60)
        print(token)
        print("=" * 60)
        
        # Save to .env
        save = input("\nSave to .env file? (y/n): ").strip().lower()
        if save == 'y':
            # Read existing DASHBOARD_URL if present
            dashboard_url = None
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('DASHBOARD_URL='):
                            dashboard_url = line.strip().split('=', 1)[1]
                            break
            except FileNotFoundError:
                pass
            
            # Write new .env file
            with open('.env', 'w') as f:
                f.write(f"API_URL={api_url}\n")
                f.write(f"JWT_TOKEN={token}\n")
                if dashboard_url:
                    f.write(f"DASHBOARD_URL={dashboard_url}\n")
                else:
                    f.write("DASHBOARD_URL=http://localhost:5173\n")
            print("\n✓ Saved to .env file!")
            print("\nYou can now run: python3 monitor_agent.py")
        else:
            print("\nManually add this to your .env file:")
            print(f"API_URL={api_url}")
            print(f"JWT_TOKEN={token}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("\n✗ Invalid email or password!")
        else:
            print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == '__main__':
    get_token()
