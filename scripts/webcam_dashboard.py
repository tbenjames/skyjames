"""
SkyJames - Webcam Dashboard
Fixed: use_column_width replaced with width
"""

import streamlit as st
import requests
import json
import time
import os
import socket

st.set_page_config(
    page_title="SkyJames Webcam",
    page_icon="📹",
    layout="wide"
)

st.markdown("""
<style>
    .webcam-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
    }
    .webcam-frame {
        border: 3px solid #4a6cf7;
        border-radius: 10px;
        max-width: 100%;
        height: auto;
    }
    .controls {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: center;
        margin: 20px 0;
    }
    .stButton > button {
        width: 100% !important;
    }
    @media (max-width: 768px) {
        .controls button {
            width: 100%;
            margin: 5px 0;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("📹 SkyJames Webcam Control")

API_URL = os.environ.get('WEBCAM_API_URL', 'http://localhost:5003')

if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'frames' not in st.session_state:
    st.session_state.frames = 0

with st.sidebar:
    st.header("🎛️ Controls")
    
    # Fixed: use_column_width instead of use_column_width
    if st.button("📷 Start Webcam", type="primary", use_column_width=True):
        try:
            response = requests.post(f"{API_URL}/webcam/start", json={'camera_id': 0})
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    st.session_state.camera_active = True
                    st.success("✅ Webcam started!")
                else:
                    st.error(f"❌ {data.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    # Fixed: use_column_width instead of use_column_width
    if st.button("🛑 Stop Webcam", use_column_width=True):
        try:
            requests.post(f"{API_URL}/webcam/stop")
            st.session_state.camera_active = False
            st.success("✅ Webcam stopped!")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    st.subheader("📹 Recording")
    duration = st.slider("Record duration (seconds)", 5, 30, 10)
    
    # Fixed: use_column_width instead of use_column_width
    if st.button("🔴 Start Recording", use_column_width=True):
        try:
            response = requests.post(f"{API_URL}/webcam/record", json={'duration': duration})
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    st.success(f"✅ Recording saved!")
                else:
                    st.error("❌ Recording failed")
        except Exception as e:
            st.error(f"❌ Error: {e}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📷 Live Feed")
    if st.session_state.camera_active:
        st.markdown(f"""
        <div class="webcam-container">
            <img src="{API_URL}/webcam/stream" class="webcam-frame" />
        </div>
        """, unsafe_allow_html=True)
        try:
            response = requests.get(f"{API_URL}/webcam/status")
            if response.status_code == 200:
                status = response.json()
                st.caption(f"FPS: {status.get('fps', 0):.1f} | Frames: {status.get('frame_count', 0)}")
        except:
            pass
    else:
        st.info("📹 Click 'Start Webcam' to begin")
        st.image("https://via.placeholder.com/640x480/1a1a2e/ffffff?text=Webcam+Offline", use_column_width=True)

with col2:
    st.subheader("📱 Mobile Access")
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        st.code(f"http://{ip_address}:8504", language="text")
        st.caption("Open this URL on your phone")
    except:
        st.info("Local IP not available")

if st.session_state.camera_active:
    time.sleep(0.1)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.8em; padding: 15px 0;">
    <p>🚀 SkyJames v2.0.0 • Webcam Ready</p>
    <p style="opacity: 0.6;">© 2024 SkyJames AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
