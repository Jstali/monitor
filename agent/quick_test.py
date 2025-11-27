#!/usr/bin/env python3
"""Quick agent startup test"""
import subprocess
import time
import signal

print("Testing agent startup...")
print("="*70)

process = subprocess.Popen(
    ['python3', 'monitor_agent.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

try:
    start = time.time()
    lines_shown = 0
    max_lines = 30
    max_time = 10
    
    while time.time() - start < max_time and lines_shown < max_lines:
        line = process.stdout.readline()
        if line:
            print(line.rstrip())
            lines_shown += 1
        if process.poll() is not None:
            break
            
finally:
    process.terminate()
    try:
        process.wait(timeout=2)
    except:
        process.kill()

print("="*70)
print("✅ Agent startup test complete")
