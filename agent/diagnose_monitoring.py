#!/usr/bin/env python3
"""
Diagnostic script to check monitoring agent functionality
"""
import subprocess
import platform
import sys
import os

def check_permissions():
    """Check if we have necessary permissions"""
    print("\n" + "="*70)
    print("1. CHECKING ACCESSIBILITY PERMISSIONS")
    print("="*70)
    
    if platform.system() == 'Darwin':  # macOS
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print(f"✅ Accessibility permissions: OK")
                print(f"   Current app detected: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Accessibility permissions: DENIED")
                print(f"   Error: {result.stderr.strip()}")
                print("\n💡 Fix: System Preferences → Security & Privacy → Privacy → Accessibility")
                print("   Add Terminal or your Python executable")
                return False
        except Exception as e:
            print(f"❌ Error checking permissions: {e}")
            return False
    return True

def check_active_window():
    """Check if we can detect active window"""
    print("\n" + "="*70)
    print("2. CHECKING ACTIVE WINDOW DETECTION")
    print("="*70)
    
    if platform.system() == 'Darwin':
        # Get application name
        app_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        try:
            result = subprocess.run(['osascript', '-e', app_script], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                app_name = result.stdout.strip()
                print(f"✅ Application detected: {app_name}")
                
                # Check if it's a browser
                browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Brave']
                if any(browser in app_name for browser in browsers):
                    print(f"   Type: Browser")
                    check_browser_url(app_name)
                else:
                    print(f"   Type: Application")
                return True
            else:
                print(f"❌ Cannot detect active window")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def check_browser_url(browser_name):
    """Check if we can get URL from browser"""
    print(f"\n   Checking URL detection for {browser_name}...")
    
    if 'Chrome' in browser_name:
        script = '''
        tell application "Google Chrome"
            if (count of windows) > 0 then
                set currentTab to active tab of front window
                return URL of currentTab & " - " & title of currentTab
            end if
        end tell
        '''
    elif 'Safari' in browser_name:
        script = '''
        tell application "Safari"
            if (count of windows) > 0 then
                set currentTab to current tab of front window
                return URL of currentTab & " - " & name of currentTab
            end if
        end tell
        '''
    elif 'Firefox' in browser_name:
        script = '''
        tell application "System Events"
            tell application process "Firefox"
                if (count of windows) > 0 then
                    return name of front window
                end if
            end tell
        end tell
        '''
    else:
        print(f"   ⚠ URL detection not configured for {browser_name}")
        return
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout.strip():
            url_info = result.stdout.strip()
            print(f"   ✅ URL detected: {url_info[:80]}...")
        else:
            print(f"   ❌ Cannot get URL: {result.stderr.strip()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_screenshot_capability():
    """Check if we can capture screenshots"""
    print("\n" + "="*70)
    print("3. CHECKING SCREENSHOT CAPABILITY")
    print("="*70)
    
    try:
        import mss
        from PIL import Image
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            print(f"✅ Screenshot capture: OK")
            print(f"   Resolution: {img.size[0]}x{img.size[1]}")
            return True
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        print("   Run: pip install mss pillow")
        return False
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        return False

def check_backend_connection():
    """Check if backend is accessible"""
    print("\n" + "="*70)
    print("4. CHECKING BACKEND CONNECTION")
    print("="*70)
    
    try:
        import requests
        from dotenv import load_dotenv
        
        load_dotenv()
        api_url = os.getenv('API_URL', 'http://localhost:5000/api')
        jwt_token = os.getenv('JWT_TOKEN')
        
        print(f"   API URL: {api_url}")
        
        # Try to ping the backend with authentication
        try:
            headers = {'Authorization': f'Bearer {jwt_token}'} if jwt_token else {}
            response = requests.get(f"{api_url}/sessions/current", headers=headers, timeout=5)
            
            if response.status_code in [200, 401]:  # 200 = OK, 401 = auth issue but server is up
                print(f"✅ Backend is reachable")
                if response.status_code == 401:
                    print(f"   ⚠ JWT token may be expired (401), but backend is running")
                return True
            else:
                print(f"⚠ Backend responded with status {response.status_code}")
                return True  # Backend is up, just different response
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to backend")
            print(f"   Make sure backend is running on {api_url}")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n" + "="*70)
    print("5. CHECKING ENVIRONMENT CONFIGURATION")
    print("="*70)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['API_URL', 'JWT_TOKEN']
    optional_vars = ['SCREENSHOT_INTERVAL', 'ACTIVITY_CHECK_INTERVAL']
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            display_value = value if var != 'JWT_TOKEN' else f"{value[:20]}..."
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_ok = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠ {var}: Using default")
    
    return all_ok

def main():
    print("\n" + "="*70)
    print("MONITORING AGENT DIAGNOSTIC TOOL")
    print("="*70)
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version.split()[0]}")
    
    results = {
        'permissions': check_permissions(),
        'window_detection': check_active_window(),
        'screenshots': check_screenshot_capability(),
        'backend': check_backend_connection(),
        'environment': check_environment()
    }
    
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check.replace('_', ' ').title()}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Agent should work correctly!")
    else:
        print("❌ SOME CHECKS FAILED - Fix the issues above before running agent")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
