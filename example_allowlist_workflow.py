"""
Complete Example: Allowlist-Based Monitoring with Process Mining

This script demonstrates the complete workflow:
1. Configure allowlist (manager)
2. Monitor activities (agent simulation)
3. Generate process mining diagram
"""

import requests
import json

# Configuration
API_URL = "http://localhost:5001/api"
MANAGER_EMAIL = "admin@example.com"  # Replace with your admin email
MANAGER_PASSWORD = "password"         # Replace with your password

def login():
    """Login and get access token"""
    response = requests.post(f"{API_URL}/auth/login", json={
        "email": MANAGER_EMAIL,
        "password": MANAGER_PASSWORD
    })
    return response.json()['access_token']

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

# ============================================================================
# STEP 1: Configure Allowlist (Manager)
# ============================================================================
def configure_allowlist(token):
    """Configure which apps/URLs to monitor"""
    print("\n" + "="*60)
    print("STEP 1: Configuring Allowlist")
    print("="*60)
    
    allowlist_items = [
        {
            "config_type": "application",
            "pattern": "Cursor",
            "folder_name": "Cursor",
            "is_active": True
        },
        {
            "config_type": "url",
            "pattern": "chatgpt.com",
            "folder_name": "ChatGPT",
            "is_active": True
        },
        {
            "config_type": "application",
            "pattern": "Slack",
            "folder_name": "Slack",
            "is_active": True
        }
    ]
    
    for item in allowlist_items:
        response = requests.post(
            f"{API_URL}/monitoring-config",
            headers=get_headers(token),
            json=item
        )
        
        if response.status_code == 201:
            print(f"✓ Added: {item['config_type']} - {item['pattern']} → {item['folder_name']}/")
        else:
            print(f"⚠ Failed to add {item['pattern']}: {response.json().get('error', 'Unknown error')}")
    
    # Display current allowlist
    response = requests.get(f"{API_URL}/monitoring-config/active", headers=get_headers(token))
    active_configs = response.json()
    
    print(f"\n📋 Active Allowlist ({len(active_configs)} items):")
    for config in active_configs:
        print(f"   - {config['config_type']}: {config['pattern']} → {config['folder_name']}/")

# ============================================================================
# STEP 2: Agent Monitoring Simulation
# ============================================================================
def simulate_agent_monitoring(token):
    """Simulate agent checking allowlist"""
    print("\n" + "="*60)
    print("STEP 2: Agent Monitoring Simulation")
    print("="*60)
    
    # Fetch allowlist (what agent does on startup)
    response = requests.get(f"{API_URL}/monitoring-config/active", headers=get_headers(token))
    allowlist = response.json()
    
    print(f"\n🤖 Agent loaded {len(allowlist)} allowlist items")
    
    # Simulate different activities
    test_activities = [
        {"app": "Cursor", "title": "main.py - Cursor", "should_capture": True, "folder": "Cursor"},
        {"app": "Google Chrome", "title": "ChatGPT - chatgpt.com", "should_capture": True, "folder": "ChatGPT"},
        {"app": "Slack", "title": "General - Slack", "should_capture": True, "folder": "Slack"},
        {"app": "Safari", "title": "YouTube - youtube.com", "should_capture": False, "folder": None},
        {"app": "Terminal", "title": "zsh", "should_capture": False, "folder": None},
    ]
    
    print("\n📊 Activity Check Results:")
    for activity in test_activities:
        # Check if activity matches allowlist
        matched = False
        folder = None
        
        for config in allowlist:
            if config['config_type'] == 'application':
                if config['pattern'].lower() in activity['app'].lower():
                    matched = True
                    folder = config['folder_name']
                    break
            elif config['config_type'] == 'url':
                if config['pattern'].lower() in activity['title'].lower():
                    matched = True
                    folder = config['folder_name']
                    break
        
        status = "✓ CAPTURE" if matched else "✗ SKIP"
        folder_info = f" → {folder}/" if folder else ""
        print(f"   {status}: {activity['app']} - {activity['title']}{folder_info}")

# ============================================================================
# STEP 3: Generate Process Mining Diagram
# ============================================================================
def generate_process_map(token, session_id=1):
    """Generate process mining diagram"""
    print("\n" + "="*60)
    print("STEP 3: Process Mining Diagram Generation")
    print("="*60)
    
    # Get process map statistics
    response = requests.get(
        f"{API_URL}/workflow/session/{session_id}/process-map?format=json",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('statistics', {})
        
        print(f"\n📈 Process Mining Statistics:")
        print(f"   Total Activities: {stats.get('total_activities', 0)}")
        print(f"   Unique Activities: {stats.get('unique_activities', 0)}")
        print(f"   Total Transitions: {stats.get('total_transitions', 0)}")
        
        print(f"\n📊 Activity Distribution:")
        for activity, count in data.get('activity_counts', {}).items():
            print(f"   - {activity}: {count} occurrences")
        
        print(f"\n🔀 Top Transitions:")
        for transition, count in list(data.get('transitions', {}).items())[:5]:
            print(f"   - {transition}: {count} times")
        
        # Download PNG diagram
        print(f"\n💾 Downloading process map diagram...")
        response = requests.get(
            f"{API_URL}/workflow/session/{session_id}/process-map?format=png",
            headers=get_headers(token)
        )
        
        if response.status_code == 200:
            with open(f'process_map_session_{session_id}.png', 'wb') as f:
                f.write(response.content)
            print(f"   ✓ Saved to: process_map_session_{session_id}.png")
        
        # Download CSV event log
        response = requests.get(
            f"{API_URL}/workflow/session/{session_id}/process-map?format=csv",
            headers=get_headers(token)
        )
        
        if response.status_code == 200:
            with open(f'event_log_session_{session_id}.csv', 'wb') as f:
                f.write(response.content)
            print(f"   ✓ Saved to: event_log_session_{session_id}.csv")
    else:
        print(f"   ⚠ Failed to generate process map: {response.json().get('error', 'Unknown error')}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Run complete example"""
    print("\n" + "="*60)
    print("Allowlist-Based Monitoring with Process Mining")
    print("="*60)
    
    try:
        # Login
        print("\n🔐 Logging in...")
        token = login()
        print("   ✓ Login successful")
        
        # Step 1: Configure allowlist
        configure_allowlist(token)
        
        # Step 2: Simulate agent monitoring
        simulate_agent_monitoring(token)
        
        # Step 3: Generate process map
        # Note: This requires actual session data
        # Uncomment when you have a session with screenshots
        # generate_process_map(token, session_id=1)
        
        print("\n" + "="*60)
        print("✓ Example completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Start the monitoring agent")
        print("2. Use Cursor and ChatGPT for a few minutes")
        print("3. Run generate_process_map() to see the workflow diagram")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
