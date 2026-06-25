"""
SkyJames - Production Monitoring Dashboard
Clean CSS style (DeepSeek-like)
"""

import streamlit as st
import psutil
import time
import requests
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="SkyJames Monitoring", layout="wide")

# ==================== CLEAN CSS (DeepSeek-like) ====================
st.markdown("""
<style>
    .stApp {
        background: #f5f6fa !important;
    }
    
    .header {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e8e8e8;
    }
    
    .header h1 {
        margin: 0;
        color: #1a1a2e;
        font-weight: 600;
    }
    
    .header h1 span {
        color: #4a6cf7;
    }
    
    .header p {
        color: #888;
        margin: 5px 0 0 0;
    }
    
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #e8e8e8;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e8e8e8;
    }
    
    .metric-card .value {
        font-size: 2em;
        font-weight: 700;
        color: #1a1a2e;
    }
    
    .metric-card .label {
        color: #888;
        font-size: 0.9em;
    }
    
    .metric-card .change {
        font-size: 0.8em;
        color: #34c759;
    }
    
    .metric-card .change.negative {
        color: #ff3b30;
    }
    
    .stButton > button {
        background: white !important;
        color: #1a1a2e !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: #f5f6fa !important;
        border-color: #4a6cf7 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74,108,247,0.12);
    }
    
    .stButton > button[kind="primary"] {
        background: #4a6cf7 !important;
        color: white !important;
        border-color: #4a6cf7 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #3a5cd7 !important;
        border-color: #3a5cd7 !important;
        box-shadow: 0 4px 16px rgba(74,108,247,0.25);
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 16px;
        font-size: 0.75em;
        font-weight: 500;
    }
    
    .status-online {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .status-offline {
        background: #fbe9e7;
        color: #c62828;
    }
    
    .status-warning {
        background: #fff3e0;
        color: #e65100;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>📊 SkyJames <span>Monitoring</span></h1>
    <p>Production System Status & Performance</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
auto_refresh = st.checkbox("Auto-refresh (every 5 seconds)", value=True)

# System metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    cpu = psutil.cpu_percent()
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{cpu}%</div>
        <div class="label">CPU Usage</div>
        <div class="change">{'🟢 Normal' if cpu < 70 else '🟡 High' if cpu < 90 else '🔴 Critical'}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    memory = psutil.virtual_memory()
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{memory.percent}%</div>
        <div class="label">Memory Usage</div>
        <div class="change">{'🟢 Normal' if memory.percent < 80 else '🟡 High' if memory.percent < 90 else '🔴 Critical'}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    disk = psutil.disk_usage('/')
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{disk.percent}%</div>
        <div class="label">Disk Usage</div>
        <div class="change">{'🟢 Normal' if disk.percent < 85 else '🟡 High' if disk.percent < 95 else '🔴 Critical'}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    uptime = time.time() - psutil.boot_time()
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{hours}h {minutes}m</div>
        <div class="label">Uptime</div>
        <div class="change">✅ System Online</div>
    </div>
    """, unsafe_allow_html=True)

# Service status
st.markdown('<div class="card"><h3 style="color: #1a1a2e;">🔌 Service Status</h3>', unsafe_allow_html=True)

services = {
    "MLflow": "http://localhost:5000",
    "API": "http://localhost:5001",
    "Dashboard": "http://localhost:8501",
    "BI Dashboard": "http://localhost:8504",
    "Webcam": "http://localhost:5003/webcam/status"
}

cols = st.columns(len(services))
for i, (name, url) in enumerate(services.items()):
    try:
        response = requests.get(url, timeout=2)
        status = "✅ Online" if response.status_code < 400 else "❌ Offline"
        badge = "status-online" if response.status_code < 400 else "status-offline"
    except:
        status = "❌ Offline"
        badge = "status-offline"
    
    with cols[i]:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px;">
            <div style="font-weight: 600; color: #1a1a2e;">{name}</div>
            <span class="status-badge {badge}">{status}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card"><h4 style="color: #1a1a2e;">📈 Resource Usage</h4>', unsafe_allow_html=True)
    times = pd.date_range(end=datetime.now(), periods=30, freq='5s')
    cpu_data = [psutil.cpu_percent() for _ in range(30)]
    memory_data = [psutil.virtual_memory().percent for _ in range(30)]
    
    df = pd.DataFrame({
        'Time': times,
        'CPU': cpu_data,
        'Memory': memory_data
    })
    
    fig = px.line(df, x='Time', y=['CPU', 'Memory'], title="Resource Usage Over Time")
    fig.update_layout(showlegend=True, height=350, paper_bgcolor='white', plot_bgcolor='white')
    st.plotly_chart(fig, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><h4 style="color: #1a1a2e;">📊 Detection Statistics</h4>', unsafe_allow_html=True)
    fig = go.Figure(data=[
        go.Bar(name='Detections', x=['Lane', 'Object', 'Safety'], y=[1247, 3456, 892], marker_color='#4a6cf7'),
        go.Scatter(name='Accuracy', x=['Lane', 'Object', 'Safety'], y=[94.2, 87.5, 92.8], yaxis='y2', line=dict(color='#34c759', width=3))
    ])
    fig.update_layout(
        title="Detection Performance",
        yaxis=dict(title="Count", gridcolor='#f0f0f0'),
        yaxis2=dict(title="Accuracy (%)", overlaying='y', side='right', gridcolor='#f0f0f0'),
        height=350,
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=True
    )
    st.plotly_chart(fig, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Alerts
st.markdown('<div class="card"><h4 style="color: #1a1a2e;">🔔 Recent Alerts</h4>', unsafe_allow_html=True)
alerts = [
    {"time": "2 min ago", "message": "CPU usage exceeded 70%", "type": "warning"},
    {"time": "15 min ago", "message": "Webcam restarted", "type": "info"},
    {"time": "1 hour ago", "message": "Model updated successfully", "type": "success"}
]

for alert in alerts:
    color = "🟡" if alert['type'] == 'warning' else "🔵" if alert['type'] == 'info' else "🟢"
    st.write(f"{color} **{alert['time']}:** {alert['message']}")

st.markdown('</div>', unsafe_allow_html=True)

if auto_refresh:
    time.sleep(5)
    st.rerun()
