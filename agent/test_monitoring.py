#!/usr/bin/env python3
"""
Test script to verify monitoring agent is working correctly
This will run the agent for 30 seconds and show what it detects
"""
import subprocess
import time
import sys
import os

def test_monitoring():
    print("="*70)
    print("MONITORING AGENT TEST")
    print("="*70)
    print("\n📋 Instructions:")
    print("   1. This test will run the monitoring agent for 30 seconds")
    print("   2. During this time, switch between different applications")
    print("   3. Open some websites in your browser")
    print("   4. The agent will show what it detects")
    print("\n" + "="*70)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        print("   Please create .env file with API_URL and JWT_TOKEN")
        return False
    
    print("\n🚀 Starting monitoring agent...")
    print("   (Running for 30 seconds)\n")
    print("="*70)
    
    try:
        # Run the agent with a timeout
        process = subprocess.Popen(
            ['python3', 'monitor_agent.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        start_time = time.time()
        duration = 30
        
        print(f"\n⏱  Test Duration: {duration} seconds")
        print("   Switch between applications to test detection!\n")
        
        # Read output for 30 seconds
        while time.time() - start_time < duration:
            line = process.stdout.readline()
            if line:
                print(line.rstrip())
            
            # Check if process ended
            if process.poll() is not None:
                break
        
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED")
        print("="*70)
        print("\n📊 What to check:")
        print("   ✓ Did the agent detect different applications?")
        print("   ✓ Did it show URLs for browser windows?")
        print("   ✓ Did it indicate which activities are in the allowlist (✓) vs not (○)?")
        print("   ✓ Did it upload screenshots for allowlisted items?")
        print("\n💡 If you saw activity detection, the agent is working!")
        print("   If not, check the error messages above.")
        print("="*70 + "\n")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        process.terminate()
        return False
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        return False

if __name__ == '__main__':
    print("\n")
    success = test_monitoring()
    sys.exit(0 if success else 1)
