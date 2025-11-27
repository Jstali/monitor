#!/usr/bin/env python3
"""
Test URL detection across different browsers
"""
import subprocess
import platform

def test_chrome():
    print("\n🔍 Testing Chrome URL Detection...")
    script = '''
    tell application "Google Chrome"
        if (count of windows) > 0 then
            set currentTab to active tab of front window
            return URL of currentTab & " - " & title of currentTab
        else
            return "No Chrome windows open"
        end if
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"✅ Chrome: {result.stdout.strip()}")
        else:
            print(f"❌ Chrome: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Chrome: {e}")

def test_firefox():
    print("\n🔍 Testing Firefox URL Detection...")
    script = '''
    tell application "System Events"
        tell application process "Firefox"
            if (count of windows) > 0 then
                return name of front window
            else
                return "No Firefox windows open"
            end if
        end tell
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"✅ Firefox: {result.stdout.strip()}")
        else:
            print(f"❌ Firefox: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Firefox: {e}")

def test_safari():
    print("\n🔍 Testing Safari URL Detection...")
    script = '''
    tell application "Safari"
        if (count of windows) > 0 then
            set currentTab to current tab of front window
            return URL of currentTab & " - " & name of currentTab
        else
            return "No Safari windows open"
        end if
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"✅ Safari: {result.stdout.strip()}")
        else:
            print(f"❌ Safari: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Safari: {e}")

def test_edge():
    print("\n🔍 Testing Edge URL Detection...")
    script = '''
    tell application "Microsoft Edge"
        if (count of windows) > 0 then
            set currentTab to active tab of front window
            return URL of currentTab & " - " & title of currentTab
        else
            return "No Edge windows open"
        end if
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"✅ Edge: {result.stdout.strip()}")
        else:
            print(f"❌ Edge: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Edge: {e}")

def test_brave():
    print("\n🔍 Testing Brave URL Detection...")
    script = '''
    tell application "Brave Browser"
        if (count of windows) > 0 then
            set currentTab to active tab of front window
            return URL of currentTab & " - " & title of currentTab
        else
            return "No Brave windows open"
        end if
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"✅ Brave: {result.stdout.strip()}")
        else:
            print(f"❌ Brave: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Brave: {e}")

if __name__ == '__main__':
    print("=" * 70)
    print("Testing URL Detection Across Browsers")
    print("=" * 70)
    print("\n📝 Instructions:")
    print("   1. Open a website in any browser (Chrome, Firefox, Safari, etc.)")
    print("   2. Run this script to test URL detection")
    print("   3. The agent will use the same method to extract URLs")
    print("\n" + "=" * 70)
    
    test_chrome()
    test_firefox()
    test_safari()
    test_edge()
    test_brave()
    
    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("\n💡 Note: Browsers that show 'No windows open' are either:")
    print("   - Not running")
    print("   - Not installed")
    print("   - Need Accessibility/Automation permissions")
    print("=" * 70)
