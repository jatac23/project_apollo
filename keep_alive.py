#!/usr/bin/env python3
"""
Keep-alive script to prevent container from restarting.
This replaces the automatic execution of main.py.
"""
import sys
import time

print("Apollo container is running in keep-alive mode.")
print("To run the labeling pipeline, execute: python main.py --run")
print("Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(60)
        print(f"Container alive at {time.strftime('%Y-%m-%d %H:%M:%S')}")
except KeyboardInterrupt:
    print("\nShutting down...")
    sys.exit(0)
