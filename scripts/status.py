"""
SkyJames Service Status Check
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

def main():
    print("🚀 SkyJames Service Status")
    print("=" * 60)
    
    check_service("MLflow", "http://localhost:5000")
    check_service("Dashboard", "http://localhost:8501")
    
    print("\n📊 Quick Commands:")
    print("  python skyjames.py --mode webcam")
    print("  python skyjames.py --mode dashboard")
    print("  streamlit run scripts/dashboard_app.py")
    
    print("\n🔗 URLs:")
    print("  MLflow: http://localhost:5000")
    print("  Dashboard: http://localhost:8501")

if __name__ == "__main__":
    main()
