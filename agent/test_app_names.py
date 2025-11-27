#!/usr/bin/env python3
"""
Test script to see what application names macOS reports
"""
import subprocess
import platform

def get_active_app():
    if platform.system() == 'Darwin':
        app_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        result = subprocess.run(['osascript', '-e', app_script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return result.stdout.strip()
    return "Unknown"

if __name__ == '__main__':
    print("Current active application:", get_active_app())
    print("\nSwitch to different applications and run this script to see their names!")
