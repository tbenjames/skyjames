"""
SkyJames - Final Model Dashboard
Fixed: use_container_width -> use_column_width for older Streamlit
"""

import streamlit as st
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="SkyJames Models", layout="wide")

st.title("🚀 SkyJames Model Selector")

# Load models without ByteTrack
@st.cache_resource
def load_models():
    from src.model_manager_no_track import load_all_models
    return load_all_models()

with st.spinner("Loading models..."):
    model_manager = load_models()

# Sidebar
with st.sidebar:
    st.header("🎯 Model Selection")
    
    available_models = model_manager.active_models if hasattr(model_manager, 'active_models') else []
    
    selected_model = st.selectbox(
        "Choose model:",
        available_models if available_models else ['No models loaded']
    )
    
    st.markdown("---")
    st.header("📊 Model Info")
    
    if selected_model in model_manager.models:
        info = model_manager.models[selected_model]
        st.write(f"**Type:** {info.get('type', 'Unknown')}")
        st.write(f"**Name:** {info.get('name', 'Unknown')}")
    
    st.markdown("---")
    st.info("""
    **Available Models:**
    - YOLO11: Object Detection
    - YOLO11-seg: Segmentation
    - YOLO11-pose: Pose Estimation
    - YOLO11-obb: Oriented BBox
    """)

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📷 Upload Image")
    
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is not None:
            # Fixed: use_column_width instead of use_container_width
            st.image(image, channels="BGR", use_column_width=True)
            
            if st.button("🔍 Detect", type="primary", use_column_width=True):
                with st.spinner(f"Running {selected_model}..."):
                    try:
                        detections = model_manager.detect(image, selected_model)
                        model_type = model_manager.models[selected_model]['type']
                        drawn = model_manager.draw_detections(image.copy(), detections, model_type)
                        
                        # Fixed: use_column_width instead of use_container_width
                        st.image(drawn, channels="BGR", use_column_width=True)
                        st.success(f"✅ Detection complete! Found {len(detections) if detections else 0} objects")
                    except Exception as e:
                        st.error(f"Error: {e}")

with col2:
    st.subheader("📊 Results Summary")
    
    if uploaded_file is not None:
        st.write("**File:**", uploaded_file.name)
        st.write("**Size:**", f"{uploaded_file.size / 1024:.1f} KB")
    
    st.markdown("---")
    st.subheader("🎯 Quick Actions")
    
    # Fixed: use_column_width instead of use_container_width
    if st.button("🔄 Reset", use_column_width=True):
        st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>SkyJames Model Manager • YOLO11 • Segmentation • Pose • OBB</p>
</div>
""", unsafe_allow_html=True)
