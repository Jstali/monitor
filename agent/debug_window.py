import time
import platform
import subprocess

def get_active_window_info():
    try:
        if platform.system() == 'Darwin':  # macOS
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
                firefox_script = '''
                tell application "System Events"
                    tell application process "Firefox"
                        if (count of windows) > 0 then
                            return name of front window
                        end if
                    end tell
                end tell
                '''
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
            
    except Exception as e:
        print(f"Error: {e}")
        return {'application': 'Unknown', 'title': ''}

print("Monitoring active window... (Press Ctrl+C to stop)")
print("-" * 60)
print(f"{'TIMESTAMP':<10} | {'APPLICATION':<20} | {'TITLE'}")
print("-" * 60)

try:
    while True:
        info = get_active_window_info()
        timestamp = time.strftime("%H:%M:%S")
        print(f"{timestamp:<10} | {info['application']:<20} | {info['title']}")
        time.sleep(2)
except KeyboardInterrupt:
    print("\nStopped.")
