"""
SkyJames - Production Monitoring Dashboard
"""

import streamlit as st
import psutil
import time
import requests
from datetime import datetime

def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "uptime": time.time() - psutil.boot_time()
    }

def get_service_status():
    services = {
        "MLflow": "http://localhost:5000",
        "API": "http://localhost:5001",
        "Dashboard": "http://localhost:8501",
        "Model Dashboard": "http://localhost:8505"
    }
    status = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            status[name] = response.status_code == 200
        except:
            status[name] = False
    return status

st.set_page_config(page_title="Production Monitor", layout="wide")

st.title("📊 SkyJames Production Monitor")

# Auto-refresh
refresh = st.checkbox("Auto-refresh (every 5 seconds)")

placeholder = st.empty()

while True:
    with placeholder.container():
        # System metrics
        col1, col2, col3, col4 = st.columns(4)
        metrics = get_system_metrics()
        
        with col1:
            st.metric("CPU Usage", f"{metrics['cpu']:.1f}%")
        with col2:
            st.metric("Memory Usage", f"{metrics['memory']:.1f}%")
        with col3:
            st.metric("Disk Usage", f"{metrics['disk']:.1f}%")
        with col4:
            uptime = int(metrics['uptime'])
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            st.metric("Uptime", f"{hours}h {minutes}m")
        
        # Service status
        st.subheader("🔌 Service Status")
        status = get_service_status()
        cols = st.columns(len(status))
        for i, (name, healthy) in enumerate(status.items()):
            with cols[i]:
                icon = "✅" if healthy else "❌"
                st.metric(name, icon)
        
        # Current time
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not refresh:
        break
    time.sleep(5)
