"""
Update the main dashboard with webcam integration
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read the dashboard file
dashboard_path = "scripts/dashboard_app.py"

if not os.path.exists(dashboard_path):
    print("Dashboard not found. Creating with webcam support...")
    # The dashboard will be created from the template below

# Create updated dashboard with webcam support
cat > scripts/dashboard_app.py << 'DASHBOARD'
"""
SkyJames - Main Dashboard with Webcam Support
"""

import streamlit as st
import cv2
import numpy as np
import os
import glob
import sys
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import time
import subprocess
import json
import shutil
import threading
import requests
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="SkyJames Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state
if 'processed_videos' not in st.session_state:
    st.session_state.processed_videos = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'video_count' not in st.session_state:
    st.session_state.video_count = 0
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False

# Custom CSS
st.markdown("""
<style>
    .clean-card {
        background: white;
        border-radius: 16px;
        padding: 25px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e8e8e8;
        transition: all 0.2s ease;
    }
    .clean-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-color: #d0d0d0;
    }
    .main-header {
        background: white;
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e8e8e8;
        text-align: center;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
        color: #1a1a2e;
        font-weight: 700;
    }
    .main-header h1 span {
        color: #4a6cf7;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        border: 1px solid #e8e8e8;
        transition: all 0.2s ease;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        border-color: #4a6cf7;
    }
    .stButton > button {
        background: white !important;
        color: #1a1a2e !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
        cursor: pointer !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    .stButton > button:hover {
        background: #f0f0f0 !important;
        border-color: #4a6cf7 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74,108,247,0.15) !important;
    }
    .stButton > button[kind="primary"] {
        background: #4a6cf7 !important;
        color: white !important;
        border-color: #4a6cf7 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #3a5cd7 !important;
        border-color: #3a5cd7 !important;
        box-shadow: 0 4px 16px rgba(74,108,247,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

def add_notification(message, type="info"):
    st.session_state.notifications.append({
        'message': message,
        'type': type,
        'time': datetime.now()
    })
    if len(st.session_state.notifications) > 50:
        st.session_state.notifications = st.session_state.notifications[-50:]

def toggle_webcam():
    if st.session_state.webcam_running:
        st.session_state.webcam_running = False
        add_notification("📹 Webcam stopped", "info")
        try:
            subprocess.run(["pkill", "-f", "webcam_api.py"], capture_output=True)
        except:
            pass
    else:
        st.session_state.webcam_running = True
        add_notification("📹 Webcam starting...", "info")
        try:
            subprocess.Popen(["python", "scripts/webcam_api.py"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            add_notification("📹 Webcam ready! Open webcam dashboard", "success")
        except Exception as e:
            add_notification(f"Error starting webcam: {str(e)[:50]}", "error")
            st.session_state.webcam_running = False

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 SkyJames <span>Dashboard</span></h1>
    <p>Computer Vision Pipeline • Webcam Ready</p>
</div>
""", unsafe_allow_html=True)

# Notifications
if st.session_state.notifications:
    with st.expander(f"🔔 Notifications ({len(st.session_state.notifications)})", expanded=False):
        for notif in st.session_state.notifications[-5:]:
            icon = "✅" if notif['type'] == 'success' else "❌" if notif['type'] == 'error' else "ℹ️"
            st.write(f"{icon} {notif['message']} *({notif['time'].strftime('%H:%M:%S')})*")

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px 0;">
        <div style="font-size: 2.5em;">🚀</div>
        <h2 style="color: #1a1a2e; margin: 5px 0;">SkyJames</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.button("🏠 Home", key="nav_home", use_column_width=True):
            st.session_state.page = "Home"
            st.rerun()
    with nav_col2:
        if st.button("🛣️ Lane", key="nav_lane", use_column_width=True):
            st.session_state.page = "Lane Detection"
            st.rerun()
    
    nav_col3, nav_col4 = st.columns(2)
    with nav_col3:
        if st.button("⚽ Sports", key="nav_sports", use_column_width=True):
            st.session_state.page = "Football Analysis"
            st.rerun()
    with nav_col4:
        if st.button("🎬 Gallery", key="nav_gallery", use_column_width=True):
            st.session_state.page = "Video Gallery"
            st.rerun()
    
    nav_col5, nav_col6 = st.columns(2)
    with nav_col5:
        if st.button("📊 Perf", key="nav_perf", use_column_width=True):
            st.session_state.page = "Performance"
            st.rerun()
    with nav_col6:
        if st.button("⚙️ Settings", key="nav_settings", use_column_width=True):
            st.session_state.page = "Settings"
            st.rerun()
    
    st.markdown("---")
    
    # Webcam Control
    st.markdown("### 📹 Webcam")
    if st.button("🎥 Open Webcam Dashboard", type="primary", use_column_width=True):
        import webbrowser
        webbrowser.open("http://localhost:8504")
        add_notification("📹 Opening webcam dashboard", "info")
    
    webcam_status = "🟢 Running" if st.session_state.webcam_running else "⚪ Stopped"
    if st.button(f"📷 Toggle Webcam ({webcam_status})", use_column_width=True):
        toggle_webcam()
        st.rerun()
    
    st.markdown("---")
    
    # Services
    if st.button("📹 Test Video (Webcam)", use_column_width=True):
        import webbrowser
        webbrowser.open("http://localhost:8504")
        add_notification("📹 Opening webcam capture", "info")
    
    # Status
    st.markdown("---")
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 12px; border-radius: 10px;">
        <p style="margin: 3px 0;">📹 Webcam: {'✅' if st.session_state.webcam_running else '❌'}</p>
        <p style="margin: 3px 0;">📊 Videos: <b>{st.session_state.video_count}</b></p>
        <p style="margin: 3px 0;">🕐 {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

# Page content
if st.session_state.page == "Home":
    st.markdown("""
    <div class="clean-card">
        <h2 style="color: #1a1a2e; margin: 0;">🏠 Dashboard Home</h2>
        <p style="color: #888;">Welcome to SkyJames - Click any card or button to interact</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2em;">🛣️</div>
            <h3>Lane Detection</h3>
            <p style="color: #888;">Active</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2em;">⚽</div>
            <h3>Sports</h3>
            <p style="color: #888;">Ready</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2em;">📹</div>
            <h3>Webcam</h3>
            <p style="color: #888;">{'✅ Active' if st.session_state.webcam_running else '⏸️ Stopped'}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2em;">🔔</div>
            <h3>Notifications</h3>
            <p style="color: #888;">{len(st.session_state.notifications)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="clean-card">
            <h3>📊 Quick Stats</h3>
        """, unsafe_allow_html=True)
        st.metric("Videos Processed", st.session_state.video_count)
        st.metric("Webcam", "Active" if st.session_state.webcam_running else "Stopped")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="clean-card">
            <h3>🚀 Quick Actions</h3>
        """, unsafe_allow_html=True)
        if st.button("📹 Open Webcam", type="primary", use_column_width=True):
            import webbrowser
            webbrowser.open("http://localhost:8504")
        if st.button("🔄 Process Sample Video", use_column_width=True):
            st.info("Processing started...")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Lane Detection":
    st.markdown("""
    <div class="clean-card">
        <h2>🛣️ Lane Detection Pipeline</h2>
        <p>Upload a video or use webcam for lane detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="clean-card">
            <h3>📤 Upload Video</h3>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a video...", type=['mp4', 'avi', 'mov', 'mkv'])
        if uploaded_file is not None:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            if st.button("🚀 Process Video", type="primary", use_column_width=True):
                st.info("Processing started...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="clean-card">
            <h3>📹 Webcam Capture</h3>
            <p>Click below to open webcam capture</p>
            <a href="http://localhost:8504" target="_blank">
                <button style="width:100%; padding:10px; background:#4a6cf7; color:white; border:none; border-radius:8px; font-size:16px; cursor:pointer;">
                    🎥 Open Webcam
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="clean-card">
            <h3>📹 Recent Results</h3>
        """, unsafe_allow_html=True)
        outputs = glob.glob("data/output/processed_nn_*.mp4")
        if outputs:
            latest = max(outputs, key=os.path.getctime)
            st.video(latest)
            st.caption(f"Latest: {os.path.basename(latest)}")
        else:
            st.info("No processed videos found")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Video Gallery":
    st.markdown("""
    <div class="clean-card">
        <h2>🎬 Video Gallery</h2>
        <p>All processed videos</p>
    </div>
    """, unsafe_allow_html=True)
    
    outputs = glob.glob("data/output/*.mp4")
    if outputs:
        cols = st.columns(2)
        for i, video in enumerate(outputs[:4]):
            with cols[i % 2]:
                st.video(video)
                st.caption(os.path.basename(video))
    else:
        st.info("No videos found")

else:
    st.info("Select a page from the sidebar")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.8em; padding: 15px 0;">
    <p>🚀 SkyJames v2.0.0 • Webcam Ready</p>
    <p style="opacity: 0.6;">© 2024 SkyJames AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
DASHBOARD

print("✅ Dashboard updated with webcam support")
