import subprocess
import sys

def check_permissions():
    print("Testing macOS Window Access Permissions...")
    
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        set frontWindow to name of front window of application process frontApp
        return frontApp & "|" & frontWindow
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("SUCCESS: Permissions are OK.")
            print(f"Current Active Window: {result.stdout.strip()}")
            return True
        else:
            print("FAILURE: Could not get active window.")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Execution failed: {e}")
        return False

if __name__ == '__main__':
    check_permissions()
