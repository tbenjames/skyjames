"""
SkyJames - Model Selection Dashboard
Choose which model to use in real-time
"""

import streamlit as st
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model_manager import load_all_models, model_manager

st.set_page_config(page_title="SkyJames Models", layout="wide")

st.title("🚀 SkyJames Model Selector")

# Load models
if 'models_loaded' not in st.session_state:
    with st.spinner("Loading models..."):
        load_all_models()
        st.session_state.models_loaded = True

# Sidebar
with st.sidebar:
    st.header("🎯 Model Selection")
    
    available_models = st.session_state.get('available_models', model_manager.active_models)
    
    selected_model = st.selectbox(
        "Choose model:",
        available_models if available_models else ['No models loaded']
    )
    
    if st.button("🔄 Reload Models"):
        load_all_models()
        st.rerun()
    
    st.markdown("---")
    st.header("📊 Model Info")
    
    if selected_model in model_manager.models:
        info = model_manager.models[selected_model]
        st.write(f"**Type:** {info.get('type', 'Unknown')}")
        st.write(f"**Name:** {info.get('name', 'Unknown')}")
        st.write(f"**Device:** {model_manager.device}")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📷 Live Feed")
    
    # Camera input
    camera_id = st.number_input("Camera ID", min_value=0, max_value=5, value=0)
    
    if st.button("📷 Start Camera"):
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                st.image(frame, channels="BGR", use_column_width=True)
                st.success("✅ Camera ready!")
            cap.release()
        else:
            st.error("❌ Could not open camera")

with col2:
    st.subheader("📊 Results")
    
    # Upload image
    uploaded_file = st.file_uploader("Or upload image", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is not None:
            st.image(image, channels="BGR", use_column_width=True)
            
            if st.button("🔍 Detect", type="primary"):
                with st.spinner(f"Running {selected_model}..."):
                    # Run detection
                    detections = model_manager.detect(image, selected_model)
                    drawn = model_manager.draw_detections(
                        image, detections, 
                        model_manager.models[selected_model]['type']
                    )
                    
                    st.image(drawn, channels="BGR", use_column_width=True)
                    st.success(f"✅ Detection complete! Found {len(detections) if detections else 0} objects")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>SkyJames Model Manager v1.0 • Supports: YOLO11, ByteTrack, TwinLiteNet+, and more</p>
</div>
""", unsafe_allow_html=True)
