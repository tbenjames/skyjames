"""
SkyJames - Model Dashboard (Direct imports)
"""

import streamlit as st
import cv2
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="SkyJames Models", layout="wide")

st.title("🚀 SkyJames Model Dashboard")

# Try to import models
try:
    from src.model_manager_no_track import load_all_models
    model_manager = load_all_models()
    st.success(f"✅ Models loaded: {model_manager.active_models}")
    models_loaded = True
except Exception as e:
    st.error(f"❌ Error loading models: {e}")
    models_loaded = False
    st.info("""
    **To fix this, make sure:**
    1. You have the model files in the right location
    2. All dependencies are installed
    3. The src directory exists
    """)

if models_loaded:
    st.markdown("---")
    st.subheader("📷 Upload Image for Detection")
    
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is not None:
            st.image(image, channels="BGR", use_column_width=True)
            
            model_name = st.selectbox("Select model:", model_manager.active_models)
            
            if st.button("🔍 Detect"):
                try:
                    detections = model_manager.detect(image, model_name)
                    model_type = model_manager.models[model_name]['type']
                    drawn = model_manager.draw_detections(image.copy(), detections, model_type)
                    
                    st.image(drawn, channels="BGR", use_column_width=True)
                    st.success(f"✅ Found {len(detections) if detections else 0} objects")
                except Exception as e:
                    st.error(f"Error during detection: {e}")
