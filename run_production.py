"""
SkyJames - Complete Production Runner
Clean CSS style (DeepSeek-like)
"""

import subprocess
import time
import signal
import sys
import os

def start_service(name, command):
    """Start a service"""
    print(f"🚀 Starting {name}...")
    try:
        process = subprocess.Popen(command, shell=True)
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    print("=" * 60)
    print("🚀 SkyJames Production System")
    print("=" * 60)
    
    # Start MLflow
    mlflow = start_service("MLflow", "mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts --host 0.0.0.0 --port 5000")
    time.sleep(3)
    
    # Start API
    api = start_service("API", "python scripts/api_server.py")
    time.sleep(2)
    
    # Start Dashboard
    dashboard = start_service("Dashboard", "streamlit run scripts/dashboard_working.py --server.port 8501 --server.headless true")
    time.sleep(2)
    
    # Start BI Dashboard
    bi = start_service("BI Dashboard", "streamlit run scripts/bi_dashboard.py --server.port 8504 --server.headless true")
    time.sleep(2)
    
    # Start Monitoring
    monitor = start_service("Monitoring", "streamlit run scripts/monitoring_dashboard.py --server.port 8505 --server.headless true")
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ All services started!")
    print("=" * 60)
    print("📊 Access URLs (Clean Design):")
    print("  - MLflow: http://localhost:5000")
    print("  - API: http://localhost:5001")
    print("  - Dashboard: http://localhost:8501")
    print("  - BI Dashboard: http://localhost:8504")
    print("  - Monitoring: http://localhost:8505")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        sys.exit(0)

if __name__ == "__main__":
    main()
