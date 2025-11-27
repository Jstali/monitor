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
                print("⚠ No allowlist configured. Capturing all activity to 'general_activity' folder.")
            
            return True
        except Exception as e:
            print(f"⚠ Failed to fetch allowlist: {e}")
            self.allowlist = []
            return False
    
    def check_allowlist(self):
        """Check if current activity matches allowlist. Returns (should_capture, folder_name, activity_name)"""
        # If no allowlist, capture everything to general_activity folder
        if not self.allowlist:
            window_info = self.get_active_window_info()
            app_name = window_info['application']
            return (True, 'general_activity', app_name)
        
        window_info = self.get_active_window_info()
        app_name = window_info['application']
        window_title = window_info['title']
        
        # DEBUG: Print what we're checking
        print(f"DEBUG: Checking app='{app_name}', title='{window_title[:50] if window_title else ''}...'")
        
        # Check each allowlist item
        for item in self.allowlist:
            if item['config_type'] == 'application':
                pattern = item['pattern'].lower()
                app_lower = app_name.lower()
                
                # More flexible matching:
                # 1. Check if pattern is in app name
                # 2. Check if app name is in pattern
                # 3. Check for common variations
                is_match = False
                
                if pattern in app_lower or app_lower in pattern:
                    is_match = True
                else:
                    # Handle common variations
                    # "Visual Studio Code" might be reported as "Code" or "Visual Studio Code"
                    pattern_words = set(pattern.split())
                    app_words = set(app_lower.split())
                    
                    # If any significant word matches (ignore common words)
                    ignore_words = {'the', 'a', 'an', 'app', 'application'}
                    pattern_words -= ignore_words
                    app_words -= ignore_words
                    
                    if pattern_words and app_words and pattern_words & app_words:
                        is_match = True
                
                if is_match:
                    print(f"DEBUG: ✓ MATCH! '{item['pattern']}' matched with '{app_name}'")
                    return (True, item['folder_name'], item['pattern'])
            
            elif item['config_type'] == 'url':
                # Check if it's a browser and URL matches
                browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Brave', 'Chromium']
                is_browser = any(browser.lower() in app_name.lower() for browser in browsers)
                
                if is_browser and window_title:
                    # Check if URL pattern is in the window title
                    # For Firefox, title might be "GitHub - Mozilla Firefox"
                    # For Chrome, title might be "https://github.com/... - Page Title"
                    
                    pattern = item['pattern'].lower()
                    title_lower = window_title.lower()
                    
                    # Remove protocol and www for easier matching
                    clean_pattern = pattern.replace('https://', '').replace('http://', '').replace('www.', '')
                    if '/' in clean_pattern:
                        clean_pattern = clean_pattern.split('/')[0]  # Just match domain
                    
                    if clean_pattern in title_lower:
                        print(f"DEBUG: ✓ URL MATCH! '{clean_pattern}' found in title")
                        return (True, item['folder_name'], item['pattern'])
        
        # Not in allowlist
        print(f"DEBUG: ✗ NOT IN ALLOWLIST - Skipping capture")
        return (False, None, None)
    
    def capture_screenshot(self):
        """Capture screenshot of ALL applications, but only upload if in allowlist"""
        try:
            # STEP 1: Capture screenshot FIRST (for all applications)
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
            
            # STEP 2: Check allowlist AFTER capture (filter before upload)
            should_capture, folder_name, activity_name = self.check_allowlist()
            
            if not should_capture:
                # Screenshot captured but NOT in allowlist
                # Delete it immediately (don't upload, don't store)
                timestamp = datetime.now().strftime('%H:%M:%S')
                window_info = self.get_active_window_info()
                print(f"  [{timestamp}] Skipped: {window_info['application']} (not in allowlist)")
                return True  # Not an error, just filtered out
            
            # STEP 3: Upload ONLY allowlist screenshots
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
            print(f"  [{timestamp}] ✓ Screenshot uploaded → {folder_name}/ ({activity_name})")
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
                
                # FIX 1: Handle Electron apps (like VS Code)
                if app_name == "Electron":
                    # Check if it's actually VS Code based on window title or process
                    # VS Code often runs as "Electron" but we can check if it's Code
                    try:
                        # Get window title first
                        title_script = '''
                        tell application "System Events"
                            tell application process "Electron"
                                if (count of windows) > 0 then
                                    return name of front window
                                end if
                            end tell
                        end tell
                        '''
                        title_result = subprocess.run(['osascript', '-e', title_script],
                                                    capture_output=True, text=True, timeout=2)
                        window_title = title_result.stdout.strip()
                        
                        # Heuristic: If title contains typical VS Code patterns
                        if "Visual Studio Code" in window_title or ".py" in window_title or ".js" in window_title or ".tsx" in window_title:
                            app_name = "Visual Studio Code"
                        else:
                            # Try to check running processes to see if it's VS Code
                            # This is a fallback
                            pass
                    except:
                        pass

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
                    # FIX 2: Improved Firefox URL detection using UI Scripting
                    # Firefox doesn't support standard AppleScript for URL, so we use UI scripting to get the address bar
                    firefox_script = '''
                    tell application "System Events"
                        tell application process "Firefox"
                            set frontWindow to front window
                            set windowTitle to name of frontWindow
                            
                            -- Try to get URL from address bar (Cmd+L usually highlights it)
                            -- This is tricky without sending keystrokes which disrupts user
                            -- So we fallback to window title which usually has "Page Title - Mozilla Firefox"
                            
                            return windowTitle
                        end tell
                    end tell
                    '''
                    firefox_result = subprocess.run(['osascript', '-e', firefox_script],
                                                  capture_output=True, text=True, timeout=2)
                    
                    if firefox_result.returncode == 0 and firefox_result.stdout.strip():
                        window_title = firefox_result.stdout.strip()
                        # Return just the title, but we can try to extract domain if possible
                        # or rely on the fact that we now know it's Firefox
                        return {'application': app_name, 'title': window_title}
                
                elif 'Edge' in app_name or 'edge' in app_name:
                    # Microsoft Edge (Chromium-based)
                    edge_script = '''
                    tell application "Microsoft Edge"
                        if (count of windows) > 0 then
                            set currentTab to active tab of front window
                            return URL of currentTab & " - " & title of currentTab
                        end if
                    end tell
                    '''
                    edge_result = subprocess.run(['osascript', '-e', edge_script],
                                               capture_output=True, text=True, timeout=2)
                    if edge_result.returncode == 0 and edge_result.stdout.strip():
                        return {'application': app_name, 'title': edge_result.stdout.strip()}
                
                elif 'Brave' in app_name or 'brave' in app_name:
                    # Brave Browser (Chromium-based)
                    brave_script = '''
                    tell application "Brave Browser"
                        if (count of windows) > 0 then
                            set currentTab to active tab of front window
                            return URL of currentTab & " - " & title of currentTab
                        end if
                    end tell
                    '''
                    brave_result = subprocess.run(['osascript', '-e', brave_script],
                                               capture_output=True, text=True, timeout=2)
                    if brave_result.returncode == 0 and brave_result.stdout.strip():
                        return {'application': app_name, 'title': brave_result.stdout.strip()}
                
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
        """Track current application/window activity (ALL APPLICATIONS)"""
        window_info = self.get_active_window_info()
        
        current_app = window_info['application']
        current_title = window_info['title']
        
        # Check for permission issue
        if current_app == 'Unknown' and current_title == '':
            print("⚠ WARNING: Unable to detect active window. Please grant Accessibility permissions to your Terminal/Python.")
            return

        # Check if app OR title changed
        if current_app != self.last_app or current_title != self.last_title:
            self.last_app = current_app
            self.last_title = current_title
            
            # Check if this activity is in allowlist (for metadata)
            should_capture, folder_name, activity_name = self.check_allowlist()
            in_allowlist = should_capture
            
            # Log activity indicator
            allowlist_indicator = "✓" if in_allowlist else "○"
            print(f"  {allowlist_indicator} Activity: {current_app} - {current_title[:50]}...")
            
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
                    window_title=current_title,  # Full window title
                    in_allowlist=in_allowlist  # NEW: Track if in allowlist
                )
            else:
                self.log_activity(
                    'application',
                    application_name=current_app,
                    window_title=current_title,
                    in_allowlist=in_allowlist  # NEW: Track if in allowlist
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
        # Open the dashboard for the user to control the session
        dashboard_url = os.getenv('DASHBOARD_URL', 'http://localhost:5173')
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
