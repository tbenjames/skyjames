"""
SkyJames - Standalone Model Dashboard
Clean model list without duplicates
"""

import streamlit as st
import cv2
import numpy as np
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="SkyJames Models", layout="wide")

st.title("🚀 SkyJames Model Dashboard")

# Initialize session state for models
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = None
if 'active_models' not in st.session_state:
    st.session_state.active_models = []

# Load models only once
if not st.session_state.models_loaded:
    with st.spinner("Loading models..."):
        try:
            from src.model_manager_no_track import load_all_models
            model_manager = load_all_models()
            st.session_state.model_manager = model_manager
            st.session_state.active_models = model_manager.active_models
            st.session_state.models_loaded = True
            st.success(f"✅ Models loaded: {len(st.session_state.active_models)} models")
        except Exception as e:
            st.error(f"Error loading models: {e}")

if st.session_state.models_loaded:
    model_manager = st.session_state.model_manager
    active_models = st.session_state.active_models
    
    # Show clean model list
    st.info(f"**Available Models:** {', '.join(active_models)}")
    
    st.markdown("---")
    st.subheader("📷 Upload Image for Detection")
    
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is not None:
            st.image(image, channels="BGR", use_column_width=True)
            
            model_name = st.selectbox("Select model:", active_models)
            
            if st.button("🔍 Detect"):
                try:
                    detections = model_manager.detect(image, model_name)
                    model_type = model_manager.models[model_name]['type']
                    drawn = model_manager.draw_detections(image.copy(), detections, model_type)
                    
                    st.image(drawn, channels="BGR", use_column_width=True)
                    if detections:
                        st.success(f"✅ Found {len(detections)} objects")
                    else:
                        st.info("No objects detected")
                except Exception as e:
                    st.error(f"Error during detection: {e}")
else:
    st.warning("Please wait for models to load...")
