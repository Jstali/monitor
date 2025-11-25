#!/usr/bin/env python3
"""
Employee Monitoring Agent
Runs on employee laptops to capture screenshots and track activity
"""

import os
import time
import threading
import requests
import psutil
import mss
from PIL import Image
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
import sys
import platform
import webbrowser

# Load environment variables
load_dotenv()

class MonitoringAgent:
    def __init__(self):
        self.api_url = os.getenv('API_URL', 'http://localhost:5000/api')
        self.email = None
        self.password = None
        self.access_token = os.getenv('JWT_TOKEN')  # Required: JWT token to fetch credentials
        self.session_id = None
        self.screenshot_interval = 10  # Default, will be updated from server
        self.running = False
        self.last_app = None
        self.last_title = None
        self.allowlist = []  # Manager-configured allowlist
        
    def fetch_credentials_from_api(self):
        """Fetch credentials from API using JWT token"""
        if not self.access_token:
            print("✗ Error: JWT_TOKEN is required. Please set it in .env file")
            print("   Get your JWT token from the Employee Dashboard after logging in")
            return False
        
        try:
            response = requests.get(
                f'{self.api_url}/monitoring/agent/credentials',
                headers={'Authorization': f'Bearer {self.access_token}'},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.email = data['email']
            self.password = data['password']
            print("✓ Fetched credentials from API")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("✗ Error: No credentials stored in dashboard")
                print("   Please go to Employee Dashboard and provide credentials when starting monitoring")
            else:
                print(f"✗ Error fetching credentials from API: {e}")
            return False
        except Exception as e:
            print(f"✗ Error fetching credentials from API: {e}")
            return False
        
    def login(self):
        """Authenticate with the backend"""
        # Fetch credentials from API (required - no .env fallback)
        if not self.fetch_credentials_from_api():
            return False
        
        # Verify we have credentials
        if not self.email or not self.password:
            return False
        
        try:
            response = requests.post(
                f'{self.api_url}/auth/login',
                json={'email': self.email, 'password': self.password},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data['access_token']
            print(f"✓ Logged in as {data['employee']['name']}")
            
            # Fetch allowlist configuration
            self.fetch_allowlist()
            
            return True
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {'Authorization': f'Bearer {self.access_token}'}
    
    def start_session(self):
        """Start a monitoring session"""
        try:
            response = requests.post(
                f'{self.api_url}/monitoring/sessions/start',
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.session_id = data['session']['id']
            self.screenshot_interval = data.get('screenshot_interval', 10)
            print(f"✓ Monitoring session started (ID: {self.session_id})")
            print(f"  Screenshot interval: {self.screenshot_interval} seconds")
            return True
        except Exception as e:
            print(f"✗ Failed to start session: {e}")
            return False
    
    def stop_session(self):
        """Stop the monitoring session"""
        try:
            response = requests.post(
                f'{self.api_url}/monitoring/sessions/stop',
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()
            print("✓ Monitoring session stopped")
            return True
        except Exception as e:
            print(f"✗ Failed to stop session: {e}")
            return False
    
    def fetch_allowlist(self):
        """Fetch manager-configured allowlist from server"""
        try:
            response = requests.get(
                f'{self.api_url}/monitoring-config/active',
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()
            self.allowlist = response.json()
            
            if self.allowlist:
                print(f"✓ Loaded {len(self.allowlist)} allowlist items:")
                for item in self.allowlist:
                    print(f"  - {item['config_type']}: {item['pattern']} → {item['folder_name']}/")
            else:
                print("⚠ No allowlist configured. Monitoring disabled.")
            
            return True
        except Exception as e:
            print(f"⚠ Failed to fetch allowlist: {e}")
            self.allowlist = []
            return False
    
    def check_allowlist(self):
        """Check if current activity matches allowlist. Returns (should_capture, folder_name, activity_name)"""
        # If no allowlist, don't capture anything
        if not self.allowlist:
            return (False, None, None)
        
        window_info = self.get_active_window_info()
        app_name = window_info['application']
        window_title = window_info['title']
        
        # DEBUG: Print what we're checking
        print(f"DEBUG: Checking app='{app_name}', title='{window_title[:50]}...'")
        
        # Check each allowlist item
        for item in self.allowlist:
            if item['config_type'] == 'application':
                # Case-insensitive application name matching
                if item['pattern'].lower() in app_name.lower():
                    print(f"DEBUG: ✓ MATCH! '{item['pattern']}' found in '{app_name}'")
                    return (True, item['folder_name'], item['pattern'])
                else:
                    print(f"DEBUG: ✗ No match: '{item['pattern']}' not in '{app_name}'")
            
            elif item['config_type'] == 'url':
                # Check if it's a browser and URL matches
                browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Brave', 'Chromium']
                is_browser = any(browser.lower() in app_name.lower() for browser in browsers)
                
                if is_browser and item['pattern'].lower() in window_title.lower():
                    print(f"DEBUG: ✓ URL MATCH! '{item['pattern']}' found in title")
                    return (True, item['folder_name'], item['pattern'])
        
        # Not in allowlist
        print(f"DEBUG: ✗ NOT IN ALLOWLIST - Skipping capture")
        return (False, None, None)
    
    def capture_screenshot(self):
        """Capture and upload screenshot (ALLOWLIST ONLY)"""
        try:
            # CHECK ALLOWLIST - Only capture if current activity is in manager's allowlist
            should_capture, folder_name, activity_name = self.check_allowlist()
            
            if not should_capture:
                # Skip - not in allowlist, do not save anything
                return True
            
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Compress and save to bytes
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG', optimize=True)
                img_bytes.seek(0)
                
                # Upload to server with folder routing metadata
                files = {'file': ('screenshot.png', img_bytes, 'image/png')}
                data = {
                    'folder_name': folder_name,
                    'activity_name': activity_name
                }
                
                response = requests.post(
                    f'{self.api_url}/screenshots/upload',
                    headers=self.get_headers(),
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"  [{timestamp}] Screenshot captured → {folder_name}/")
                return True
                
        except Exception as e:
            print(f"✗ Screenshot capture failed: {e}")
            return False
    
    def get_active_window_info(self):
        """Get information about the active window"""
        try:
            if platform.system() == 'Darwin':  # macOS
                import subprocess
                
                # First, get the active application
                app_script = '''
                tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                    return frontApp
                end tell
                '''
                app_result = subprocess.run(['osascript', '-e', app_script], 
                                          capture_output=True, text=True, timeout=2)
                
                if app_result.returncode != 0:
                    return {'application': 'Unknown', 'title': ''}
                
                app_name = app_result.stdout.strip()
                
                # For browsers, try to get the actual URL
                if 'Chrome' in app_name or 'Chromium' in app_name:
                    url_script = '''
                    tell application "Google Chrome"
                        if (count of windows) > 0 then
                            set currentTab to active tab of front window
                            return URL of currentTab & " - " & title of currentTab
                        end if
                    end tell
                    '''
                    url_result = subprocess.run(['osascript', '-e', url_script],
                                              capture_output=True, text=True, timeout=2)
                    if url_result.returncode == 0 and url_result.stdout.strip():
                        return {'application': app_name, 'title': url_result.stdout.strip()}
                
                elif 'Safari' in app_name:
                    url_script = '''
                    tell application "Safari"
                        if (count of windows) > 0 then
                            set currentTab to current tab of front window
                            return URL of currentTab & " - " & name of currentTab
                        end if
                    end tell
                    '''
                    url_result = subprocess.run(['osascript', '-e', url_script],
                                              capture_output=True, text=True, timeout=2)
                    if url_result.returncode == 0 and url_result.stdout.strip():
                        return {'application': app_name, 'title': url_result.stdout.strip()}
                
                elif 'Firefox' in app_name or 'firefox' in app_name:
                    # Firefox doesn't support direct URL access via AppleScript easily
                    # We'll try to get the window title which often contains the page title
                    firefox_script = '''
                    tell application "System Events"
                        tell application process "Firefox"
                            if (count of windows) > 0 then
                                return name of front window
                            end if
                        end tell
                    end tell
                    '''
                    # Try with lowercase if uppercase fails
                    firefox_result = subprocess.run(['osascript', '-e', firefox_script],
                                                  capture_output=True, text=True, timeout=2)
                    
                    if firefox_result.returncode == 0 and firefox_result.stdout.strip():
                        return {'application': app_name, 'title': firefox_result.stdout.strip()}
                
                # For other apps, try to get window title
                window_script = f'''
                tell application "System Events"
                    tell application process "{app_name}"
                        if (count of windows) > 0 then
                            return name of front window
                        end if
                    end tell
                end tell
                '''
                window_result = subprocess.run(['osascript', '-e', window_script],
                                             capture_output=True, text=True, timeout=2)
                
                window_title = window_result.stdout.strip() if window_result.returncode == 0 else ''
                return {'application': app_name, 'title': window_title}
                
            elif platform.system() == 'Windows':
                # Use pygetwindow for Windows
                import pygetwindow as gw
                active = gw.getActiveWindow()
                if active:
                    return {
                        'application': active.title.split('-')[-1].strip() if '-' in active.title else active.title,
                        'title': active.title
                    }
            elif platform.system() == 'Linux':
                # Use wmctrl for Linux
                import subprocess
                result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    title = result.stdout.strip()
                    return {
                        'application': title.split('-')[-1].strip() if '-' in title else title,
                        'title': title
                    }
        except Exception as e:
            print(f"DEBUG: get_active_window_info failed: {e}")
            pass
        
        return {'application': 'Unknown', 'title': ''}
    
    def log_activity(self, activity_type, **kwargs):
        """Log an activity to the server"""
        try:
            data = {
                'activity_type': activity_type,
                **kwargs
            }
            response = requests.post(
                f'{self.api_url}/monitoring/activities',
                headers=self.get_headers(),
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"✗ Failed to log activity: {e}")
            return False
    
    def track_activity(self):
        """Track current application/window activity (ALLOWLIST ONLY)"""
        # CHECK ALLOWLIST - Only track if current activity is in manager's allowlist
        should_capture, folder_name, activity_name = self.check_allowlist()
        
        if not should_capture:
            # Skip - not in allowlist
            return

        window_info = self.get_active_window_info()
        
        current_app = window_info['application']
        current_title = window_info['title']
        
        # Check for permission issue
        if current_app == 'Unknown' and current_title == '':
            # Only warn if we expected to capture something (which we did, since check_allowlist passed)
            # But check_allowlist calls get_active_window_info internally, so this might be redundant
            # keeping it for safety
            print("⚠ WARNING: Unable to detect active window. Please grant Accessibility permissions to your Terminal/Python.")
            return

        # Check if app OR title changed
        if current_app != self.last_app or current_title != self.last_title:
            self.last_app = current_app
            self.last_title = current_title
            
            print(f"  Activity: {current_app} - {current_title}")
            
            # Determine if it's a browser (website) or application
            browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Brave']
            is_browser = any(browser.lower() in current_app.lower() 
                           for browser in browsers)
            
            if is_browser:
                # Try to extract URL from window title
                url = current_title.split('-')[0].strip() if '-' in current_title else current_title
                self.log_activity(
                    'website',
                    application_name=current_app,  # Add browser name
                    url=url,
                    window_title=current_title  # Full window title
                )
            else:
                self.log_activity(
                    'application',
                    application_name=current_app,
                    window_title=current_title
                )
    
    def screenshot_loop(self):
        """Background thread for screenshot capture"""
        while self.running:
            self.capture_screenshot()
            time.sleep(self.screenshot_interval)
    
    def activity_loop(self):
        """Background thread for activity tracking"""
        while self.running:
            self.track_activity()
            time.sleep(5)  # Check activity every 5 seconds
    
    def check_session_status(self):
        """Check if there is an active session for this employee"""
        try:
            response = requests.get(
                f'{self.api_url}/monitoring/sessions/current',
                headers=self.get_headers(),
                timeout=10
            )
            
            # Handle token expiration
            if response.status_code == 401:
                print("⚠ Token expired, re-authenticating...")
                if self.login():
                    # Retry with new token
                    response = requests.get(
                        f'{self.api_url}/monitoring/sessions/current',
                        headers=self.get_headers(),
                        timeout=10
                    )
                else:
                    return None
            
            if response.status_code == 200:
                data = response.json()
                # print(f"DEBUG: Polling response: {data}") # Uncomment for verbose debugging
                
                # Handle both {session: {...}} and direct session object formats
                session = data.get('session') or data
                
                if session and session.get('is_active'):
                    return session
            else:
                print(f"DEBUG: Polling failed with status {response.status_code}")
            
            return None
        except Exception as e:
            # Don't print error on every poll to avoid spamming
            return None

    def start(self):
        """Start the agent"""
        print(f"Agent starting (PID: {os.getpid()})...")
        
        if not self.login():
            return

        # Open the dashboard for the user to control the session
        dashboard_url = "http://localhost:5173"
        print(f"Opening dashboard at {dashboard_url}...")
        webbrowser.open(dashboard_url)
        
        print("\n✓ Agent ready. Waiting for monitoring session...")
        print("  Start monitoring from the Web Dashboard.")
        print("  Press Ctrl+C to exit agent\n")
        
        # Track last allowlist refresh time
        last_allowlist_refresh = time.time()
        ALLOWLIST_REFRESH_INTERVAL = 30  # Refresh every 30 seconds
        
        try:
            while True:
                # Periodically refresh allowlist to pick up new configurations
                current_time = time.time()
                if current_time - last_allowlist_refresh >= ALLOWLIST_REFRESH_INTERVAL:
                    old_count = len(self.allowlist) if self.allowlist else 0
                    self.fetch_allowlist()
                    new_count = len(self.allowlist) if self.allowlist else 0
                    
                    if new_count != old_count:
                        print(f"  🔄 Allowlist updated: {old_count} → {new_count} items")
                    
                    last_allowlist_refresh = current_time
                
                # Check for active session
                active_session = self.check_session_status()
                
                if active_session:
                    if not self.running:
                        # Session started remotely
                        self.session_id = active_session['id']
                        self.screenshot_interval = active_session.get('screenshot_interval', 10)
                        self.running = True
                        
                        print(f"\n✓ Active session detected (ID: {self.session_id})")
                        print(f"  Screenshot interval: {self.screenshot_interval} seconds")
                        print("  Starting capture...")
                        
                        # Start background threads
                        self.screenshot_thread = threading.Thread(target=self.screenshot_loop, daemon=True)
                        self.activity_thread = threading.Thread(target=self.activity_loop, daemon=True)
                        
                        self.screenshot_thread.start()
                        self.activity_thread.start()
                    else:
                        # Update interval if changed
                        new_interval = active_session.get('screenshot_interval', 10)
                        if new_interval != self.screenshot_interval:
                            self.screenshot_interval = new_interval
                            print(f"  Updated screenshot interval: {self.screenshot_interval}s")
                
                elif self.running:
                    # Session stopped remotely
                    print("\n✓ Session ended remotely. Stopping capture...")
                    self.running = False
                    # Threads will exit because self.running is False
                    print("  Waiting for next session...")
                
                # Poll every 5 seconds
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\nExiting agent...")
            self.running = False
            print("✓ Agent exited\n")
        
        return True

def main():
    """Main entry point"""
    agent = MonitoringAgent()
    
    # JWT_TOKEN is required to fetch credentials from API
    if not agent.access_token:
        print("=" * 60)
        print("ERROR: JWT_TOKEN is required in .env file")
        print("=" * 60)
        print("\nTo get your JWT token:")
        print("  1. Log in to the Employee Dashboard")
        print("  2. Open browser Developer Tools (F12)")
        print("  3. Go to Application/Storage > Local Storage")
        print("  4. Copy the 'token' value")
        print("  5. Add it to agent/.env as: JWT_TOKEN=your_token_here")
        print("\nAlternatively, you can:")
        print("  - Start monitoring from the dashboard (credentials will be stored)")
        print("  - Then run the agent with JWT_TOKEN set")
        print("\nNote: Credentials are now managed through the dashboard only.")
        print("      No need to set EMAIL and PASSWORD in .env anymore.")
        print("=" * 60)
        sys.exit(1)
    
    # Fetch credentials from API (required)
    if not agent.fetch_credentials_from_api():
        print("\n" + "=" * 60)
        print("ERROR: Could not fetch credentials from API")
        print("=" * 60)
        print("\nPlease ensure:")
        print("  1. You have provided credentials in the Employee Dashboard")
        print("  2. Your JWT_TOKEN is valid and not expired")
        print("  3. The backend API is accessible")
        print("\nTo set credentials:")
        print("  - Log in to Employee Dashboard")
        print("  - Click 'Start Monitoring'")
        print("  - Enter your email and password in the modal")
        print("=" * 60)
        sys.exit(1)
    
    agent.start()

if __name__ == '__main__':
    main()
