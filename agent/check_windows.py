#!/usr/bin/env python3
"""Check what windows are currently active"""
import sys
import platform

def get_active_window_info():
    """Get information about the active window"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        try:
            from AppKit import NSWorkspace
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID
            )
            
            # Get all on-screen windows
            windows = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID
            )
            
            print("=" * 80)
            print("ALL VISIBLE WINDOWS:")
            print("=" * 80)
            
            for i, window in enumerate(windows[:20]):  # Show first 20
                owner = window.get('kCGWindowOwnerName', 'Unknown')
                name = window.get('kCGWindowName', 'No Title')
                layer = window.get('kCGWindowLayer', 0)
                
                if layer == 0:  # Normal windows
                    print(f"\n{i+1}. Application: {owner}")
                    print(f"   Window Title: {name}")
                    print(f"   Layer: {layer}")
            
            # Get active application
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            print("\n" + "=" * 80)
            print("CURRENTLY ACTIVE APPLICATION:")
            print("=" * 80)
            print(f"Name: {active_app['NSApplicationName']}")
            print(f"Bundle ID: {active_app.get('NSApplicationBundleIdentifier', 'N/A')}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print(f"Unsupported system: {system}")

if __name__ == "__main__":
    get_active_window_info()
