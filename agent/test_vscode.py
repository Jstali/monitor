#!/usr/bin/env python3
"""
Test VS Code detection
"""
import subprocess
import time

def test_vscode_detection():
    print("="*70)
    print("VS CODE DETECTION TEST")
    print("="*70)
    print("Please focus VS Code now! (You have 5 seconds)")
    
    for i in range(5, 0, -1):
        print(f"Checking in {i}...")
        time.sleep(1)
        
    print("\nChecking active window...")
    
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        return frontApp
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    app_name = result.stdout.strip()
    print(f"Raw App Name: '{app_name}'")
    
    if app_name == "Electron":
        print("⚠ Detected as Electron. Trying to identify as VS Code...")
        
        title_script = '''
        tell application "System Events"
            tell application process "Electron"
                if (count of windows) > 0 then
                    return name of front window
                end if
            end tell
        end tell
        '''
        title_result = subprocess.run(['osascript', '-e', title_script], capture_output=True, text=True)
        window_title = title_result.stdout.strip()
        print(f"Window Title: '{window_title}'")
        
        if "Visual Studio Code" in window_title or ".py" in window_title or ".js" in window_title:
            print("✅ CORRECTLY IDENTIFIED AS: Visual Studio Code")
        else:
            print("❌ Could not confirm it is VS Code")
            
    elif app_name == "Visual Studio Code" or app_name == "Code":
        print("✅ CORRECTLY IDENTIFIED AS: Visual Studio Code")
    else:
        print(f"ℹ Detected as: {app_name}")

if __name__ == '__main__':
    test_vscode_detection()
