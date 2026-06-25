#!/usr/bin/env python
"""
SkyJames Advanced Features Launcher (Fixed)
"""

import subprocess
import time
import sys
import os
import signal

def start_mlflow():
    print("📊 Starting MLflow on port 5000...")
    subprocess.Popen([
        "mlflow", "server", 
        "--backend-store-uri", "sqlite:///mlflow.db",
        "--default-artifact-root", "./mlflow_artifacts",
        "--host", "0.0.0.0",
        "--port", "5000"
    ])
    time.sleep(3)

def start_api():
    print("🌐 Starting API server on port 5001...")
    subprocess.Popen(["python", "scripts/api_server.py"])
    time.sleep(2)

def start_streaming():
    print("📡 Starting WebRTC streaming on port 8766...")
    subprocess.Popen(["python", "src/webrtc_stream.py"])

def start_scheduler():
    print("⏰ Starting task scheduler...")
    subprocess.Popen(["python", "src/scheduler.py"])

def start_dashboard():
    print("📊 Starting main dashboard on port 8501...")
    subprocess.Popen([
        "streamlit", "run", "scripts/dashboard_app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ])
    time.sleep(2)

def start_analytics():
    print("📈 Starting analytics dashboard on port 8503...")
    subprocess.Popen([
        "streamlit", "run", "scripts/analytics_dashboard.py",
        "--server.port", "8503",
        "--server.headless", "true"
    ])
    time.sleep(2)

def main():
    print("=" * 60)
    print("🚀 SkyJames Advanced Features (Fixed)")
    print("=" * 60)
    
    # Start services with new ports
    start_mlflow()
    start_api()
    start_streaming()
    start_scheduler()
    start_dashboard()
    start_analytics()
    
    print("\n" + "=" * 60)
    print("✅ All services started!")
    print("=" * 60)
    print("📊 Services:")
    print("  - MLflow: http://localhost:5000")
    print("  - Dashboard: http://localhost:8501")
    print("  - Analytics: http://localhost:8503")
    print("  - WebRTC: ws://localhost:8766")
    print("  - API: http://localhost:5001")
    print("  - Scheduler: Running in background")
    print("=" * 60)
    print("\nPress Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        sys.exit(0)

if __name__ == "__main__":
    main()
