#!/usr/bin/env python3
"""
Simple Employee Monitoring Agent
Runs with email/password authentication
"""

import os
import time
import threading
import requests
import mss
from PIL import Image
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
import platform

# Load environment variables
load_dotenv()

class SimpleMonitoringAgent:
    def __init__(self):
        self.api_url = os.getenv('API_URL', 'http://localhost:3535/api')
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.access_token = None
        self.session_id = None
        self.screenshot_interval = 60  # Default 60 seconds
        self.running = False
        self.last_app = None
        
    def login(self):
        """Authenticate with the backend"""
        if not self.email or not self.password:
            print("✗ Error: EMAIL and PASSWORD must be set in .env file")
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
            headers = self.get_headers()
            headers['Content-Type'] = 'application/json'
            response = requests.post(
                f'{self.api_url}/monitoring/sessions/start',
                headers=headers,
                json={},  # Send empty JSON object
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.session_id = data['session']['id']
            self.screenshot_interval = data.get('screenshot_interval', 60)
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
                data = {
                    'folder_name': 'general_activity',
                    'activity_name': 'General Activity'
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
                print(f"  [{timestamp}] Screenshot captured")
                return True
                
        except Exception as e:
            print(f"✗ Screenshot capture failed: {e}")
            return False
    
    def get_active_window_info(self):
        """Get information about the active window"""
        try:
            if platform.system() == 'Darwin':  # macOS
                import subprocess
                
                # Get the active application
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
                
                # For Chrome, try to get URL
                if 'Chrome' in app_name:
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
                
                # For other apps, get window title
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
                
        except Exception as e:
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
        
        # Only log if app changed
        if current_app != self.last_app:
            self.last_app = current_app
            
            print(f"  Activity: {current_app} - {current_title[:50]}")
            
            # Determine if it's a browser (website) or application
            browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Brave']
            is_browser = any(browser.lower() in current_app.lower() for browser in browsers)
            
            if is_browser:
                url = current_title.split('-')[0].strip() if '-' in current_title else current_title
                self.log_activity(
                    'website',
                    application_name=current_app,
                    url=url,
                    window_title=current_title
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
    
    def start(self):
        """Start the agent"""
        print("=" * 60)
        print("Simple Monitoring Agent")
        print("=" * 60)
        
        # Login
        if not self.login():
            return
        
        # Start session
        if not self.start_session():
            return
        
        # Start monitoring
        self.running = True
        
        print("\n✓ Monitoring started!")
        print("  Press Ctrl+C to stop\n")
        
        # Start background threads
        screenshot_thread = threading.Thread(target=self.screenshot_loop, daemon=True)
        activity_thread = threading.Thread(target=self.activity_loop, daemon=True)
        
        screenshot_thread.start()
        activity_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping monitoring...")
            self.running = False
            self.stop_session()
            print("✓ Agent stopped\n")

def main():
    agent = SimpleMonitoringAgent()
    agent.start()

if __name__ == '__main__':
    main()
