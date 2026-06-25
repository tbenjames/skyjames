#!/usr/bin/env python
"""
SkyJames System Health Check
"""

import requests
import subprocess
import sys

def check_service(name, url, expected_status=200):
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == expected_status:
            print(f"✅ {name}: Running on {url}")
            return True
        else:
            print(f"⚠️ {name}: Status {response.status_code}")
            return False
    except:
        print(f"❌ {name}: Not running")
        return False

def check_process(name, pattern):
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        if pattern in result.stdout:
            print(f"✅ {name}: Running")
            return True
        else:
            print(f"❌ {name}: Not running")
            return False
    except:
        print(f"❌ {name}: Check failed")
        return False

def main():
    print("=" * 60)
    print("🩺 SkyJames System Health Check")
    print("=" * 60)
    
    # Check web services
    check_service("MLflow", "http://localhost:5000")
    check_service("Dashboard", "http://localhost:8501")
    check_service("Analytics", "http://localhost:8502")
    check_service("API", "http://localhost:5000/status")
    
    # Check background processes
    check_process("WebRTC", "webrtc_stream")
    check_process("Scheduler", "scheduler")
    
    print("=" * 60)
    print("📊 Enterprise Features:")
    
    # Check enterprise modules
    try:
        from src.enterprise import SkyJamesMLflow, metrics, ABTesting, BIExporter
        print("✅ Enterprise modules: Loaded")
    except:
        print("❌ Enterprise modules: Not loaded")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
