"""
SkyJames System Test
"""

import requests
import json
import sys

def test_services():
    print("🚀 Testing SkyJames Services")
    print("=" * 50)
    
    # Test MLflow
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        print(f"✅ MLflow: {response.status_code}")
    except:
        print("❌ MLflow: Not running")
    
    # Test Dashboard
    try:
        response = requests.get("http://localhost:8501", timeout=2)
        print(f"✅ Dashboard: {response.status_code}")
    except:
        print("❌ Dashboard: Not running")
    
    # Test API
    try:
        response = requests.get("http://localhost:5000/status", timeout=2)
        print(f"✅ API: {response.status_code}")
    except:
        print("❌ API: Not running")
    
    print("=" * 50)

if __name__ == "__main__":
    test_services()
