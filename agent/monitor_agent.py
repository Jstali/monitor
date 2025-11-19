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
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.access_token = None
        self.session_id = None
        self.screenshot_interval = 10  # Default, will be updated from server
        self.running = False
        self.last_app = None
        self.last_title = None
        
    def login(self):
        """Authenticate with the backend"""
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
    
    def capture_screenshot(self):
        """Capture and upload screenshot"""
        try:
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
                
                # Upload to server
                files = {'file': ('screenshot.png', img_bytes, 'image/png')}
                response = requests.post(
                    f'{self.api_url}/screenshots/upload',
                    headers=self.get_headers(),
                    files=files,
                    timeout=30
                )
                response.raise_for_status()
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"  [{timestamp}] Screenshot captured and uploaded")
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
        """Track current application/window activity"""
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
        
        try:
            while True:
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
    
    if not agent.email or not agent.password:
        print("Error: EMAIL and PASSWORD must be set in .env file")
        print("Copy .env.example to .env and configure your credentials")
        sys.exit(1)
    
    agent.start()

if __name__ == '__main__':
    main()
