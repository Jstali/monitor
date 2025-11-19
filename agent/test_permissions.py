#!/usr/bin/env python3
"""
Test if the agent can capture window information
This will help diagnose the permissions issue
"""
import subprocess

def test_window_capture():
    print("=" * 60)
    print("TESTING WINDOW INFORMATION CAPTURE")
    print("=" * 60)
    
    print("\n[1/2] Testing AppleScript access...")
    try:
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            set frontWindow to name of front window of application process frontApp
            return frontApp & " - " & frontWindow
        end tell
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✓ SUCCESS: {result.stdout.strip()}")
            print("  Accessibility permissions are granted!")
        else:
            print(f"✗ FAILED: {result.stderr.strip()}")
            print("\n⚠ PERMISSION ISSUE DETECTED!")
            print("\nTo fix:")
            print("1. Open System Settings")
            print("2. Go to Privacy & Security → Accessibility")
            print("3. Find 'Terminal' (or your terminal app)")
            print("4. Enable the checkbox")
            print("5. Restart the agent")
            return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    
    print("\n[2/2] Testing Python implementation...")
    try:
        from agent.monitor_agent import MonitoringAgent
        agent = MonitoringAgent()
        info = agent.get_active_window_info()
        
        print(f"Application: {info.get('application_name', 'Unknown')}")
        print(f"Window Title: {info.get('window_title', 'Unknown')}")
        
        if info.get('application_name') and info.get('application_name') != 'Unknown':
            print("\n✓ Agent can capture window information!")
            return True
        else:
            print("\n✗ Agent cannot capture window information")
            print("  Check permissions above")
            return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

if __name__ == '__main__':
    success = test_window_capture()
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("The agent should be able to capture real activity data")
    else:
        print("✗ TESTS FAILED")
        print("Fix the permissions issue above and try again")
    print("=" * 60)
