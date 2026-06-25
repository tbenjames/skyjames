"""
SkyJames - Simple Model Dashboard
Fixed: Proper path handling for imports
"""

import streamlit as st
import cv2
import numpy as np
import sys
import os

# Add parent directory to path so src can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="SkyJames Models", layout="wide")

st.title("🚀 SkyJames Model Dashboard")

st.info("""
**Available Models:**
- YOLO11: Object Detection
- YOLO11-seg: Segmentation  
- YOLO11-pose: Pose Estimation
- YOLO11-obb: Oriented BBox
""")

# File upload
uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # Read image
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if image is not None:
        st.image(image, channels="BGR", use_column_width=True)
        
        # Model selection
        model_name = st.selectbox(
            "Select model:",
            ["yolo", "yolo_seg", "yolo_pose", "yolo_obb"]
        )
        
        if st.button("🔍 Detect"):
            try:
                # Import models here (lazy loading)
                from src.model_manager_no_track import load_all_models
                model_manager = load_all_models()
                
                detections = model_manager.detect(image, model_name)
                model_type = model_manager.models[model_name]['type']
                drawn = model_manager.draw_detections(image.copy(), detections, model_type)
                
                st.image(drawn, channels="BGR", use_column_width=True)
                st.success(f"✅ Found {len(detections) if detections else 0} objects")
            except Exception as e:
                st.error(f"Error: {e}")
