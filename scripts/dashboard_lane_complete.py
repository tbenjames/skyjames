"""
SkyJames - Complete Lane Detection with Image & Video Support
Upload images and videos, detect objects, show frame info
"""

import streamlit as st
import cv2
import numpy as np
import os
import sys
import time
from PIL import Image
import io
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page config
st.set_page_config(
    page_title="SkyJames - Lane Detection",
    page_icon="🚀",
    layout="wide"
)

# ==================== SESSION STATE ====================
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False
if 'video_count' not in st.session_state:
    st.session_state.video_count = 0
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
if 'notification' not in st.session_state:
    st.session_state.notification = ""
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = None
if 'active_models' not in st.session_state:
    st.session_state.active_models = []
if 'detections' not in st.session_state:
    st.session_state.detections = []
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'uploaded_video' not in st.session_state:
    st.session_state.uploaded_video = None
if 'processed_frames' not in st.session_state:
    st.session_state.processed_frames = []
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0
if 'processing' not in st.session_state:
    st.session_state.processing = False

# ==================== HELPER FUNCTIONS ====================
def notify(msg):
    st.session_state.notification = msg

def load_models():
    try:
        from src.model_manager_no_track import load_all_models
        model_manager = load_all_models()
        st.session_state.model_manager = model_manager
        st.session_state.active_models = model_manager.active_models
        st.session_state.models_loaded = True
        notify(f"✅ {len(st.session_state.active_models)} models loaded!")
        return True
    except Exception as e:
        notify(f"❌ Error loading models: {e}")
        return False

def process_image(image, model_name):
    try:
        model_manager = st.session_state.model_manager
        detections = model_manager.detect(image, model_name)
        model_type = model_manager.models[model_name]['type']
        drawn = model_manager.draw_detections(image.copy(), detections, model_type)
        st.session_state.detections = detections
        return drawn, detections
    except Exception as e:
        notify(f"❌ Detection error: {e}")
        return image, []

def process_video_frames(video_path, model_name, max_frames=50):
    """Process video and extract frames with detections"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            notify("❌ Could not open video")
            return [], 0
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        processed_frames = []
        detections_count = 0
        
        model_manager = st.session_state.model_manager
        
        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects
            detections = model_manager.detect(frame, model_name)
            model_type = model_manager.models[model_name]['type']
            drawn = model_manager.draw_detections(frame.copy(), detections, model_type)
            
            # Store frame info
            processed_frames.append({
                'frame': drawn,
                'number': frame_count,
                'detections': detections,
                'count': len(detections)
            })
            
            detections_count += len(detections)
            frame_count += 1
        
        cap.release()
        
        st.session_state.frame_count = frame_count
        st.session_state.processed_frames = processed_frames
        st.session_state.detections = []
        
        return processed_frames, detections_count
    except Exception as e:
        notify(f"❌ Video processing error: {e}")
        return [], 0

# ==================== CSS ====================
st.markdown("""
<style>
    .stApp { background: #f5f6fa !important; }
    .header {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e8e8e8;
    }
    .header h1 { margin: 0; color: #1a1a2e; }
    .header h1 span { color: #4a6cf7; }
    .header p { color: #888; margin: 5px 0 0 0; }
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #e8e8e8;
    }
    .card:hover {
        border-color: #4a6cf7;
    }
    .metric {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e8e8e8;
    }
    .metric .icon { font-size: 2em; }
    .metric .value { font-size: 1.5em; font-weight: bold; color: #1a1a2e; }
    .metric .label { color: #888; }
    .stButton > button {
        width: 100% !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: #4a6cf7 !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #3a5cd7 !important;
    }
    .stButton > button[kind="secondary"] {
        background: #e8e8e8 !important;
        color: #1a1a2e !important;
    }
    .notification {
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        background: #e8f5e9;
        border-left: 4px solid #34c759;
    }
    .notification.error {
        background: #fbe9e7;
        border-left-color: #ff3b30;
    }
    .notification.warning {
        background: #fff3e0;
        border-left-color: #ff9500;
    }
    .upload-area {
        border: 2px dashed #d0d0d0;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .upload-area:hover {
        border-color: #4a6cf7;
        background: #f8f9fa;
    }
    .frame-slider {
        padding: 10px 0;
    }
    .detection-info {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="header">
    <h1>🚀 SkyJames <span>Lane Detection</span></h1>
    <p>Upload Images & Videos • Object Detection • Frame Analysis</p>
</div>
""", unsafe_allow_html=True)

# ==================== NOTIFICATION ====================
if st.session_state.notification:
    notif_class = "notification"
    if "❌" in st.session_state.notification:
        notif_class += " error"
    elif "⚠️" in st.session_state.notification:
        notif_class += " warning"
    st.markdown(f'<div class="{notif_class}">{st.session_state.notification}</div>', unsafe_allow_html=True)
    st.session_state.notification = ""

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🚀 SkyJames")
    st.markdown("---")
    
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
        st.rerun()
    
    if st.button("📹 Webcam"):
        st.session_state.page = "Webcam"
        st.rerun()
    
    if st.button("🛣️ Lane Detection"):
        st.session_state.page = "Lane"
        st.rerun()
    
    if st.button("🤖 Models"):
        st.session_state.page = "Models"
        st.rerun()
    
    if st.button("⚙️ Settings"):
        st.session_state.page = "Settings"
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"**Videos:** {st.session_state.video_count}")
    st.markdown(f"**Models:** {'✅ Loaded' if st.session_state.models_loaded else '❌ Not Loaded'}")
    st.markdown(f"**Frames:** {st.session_state.frame_count}")

# ==================== HOME ====================
if st.session_state.page == "Home":
    st.markdown("### Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric">
            <div class="icon">🛣️</div>
            <div class="value">Active</div>
            <div class="label">Lane Detection</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric">
            <div class="icon">📊</div>
            <div class="value">{st.session_state.video_count}</div>
            <div class="label">Videos Processed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric">
            <div class="icon">🎯</div>
            <div class="value">{len(st.session_state.active_models) if st.session_state.models_loaded else 0}</div>
            <div class="label">Models</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛣️ Open Lane Detection", type="primary"):
            st.session_state.page = "Lane"
            st.rerun()
    with col2:
        if st.button("🤖 Load Models", type="primary"):
            load_models()
            st.rerun()

# ==================== LANE DETECTION ====================
elif st.session_state.page == "Lane":
    st.markdown("### 🛣️ Lane Detection")
    st.caption("Upload images or videos for object detection")
    
    # Check if models are loaded
    if not st.session_state.models_loaded:
        st.warning("⚠️ Models not loaded. Click below to load.")
        if st.button("🔄 Load Models", type="primary"):
            load_models()
            st.rerun()
        st.stop()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Upload Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📤 Upload File")
        
        # File uploader - supports both images and videos
        uploaded_file = st.file_uploader(
            "Choose an image or video...",
            type=['jpg', 'jpeg', 'png', 'bmp', 'mp4', 'avi', 'mov', 'mkv', 'webm'],
            help="Supported: Images (jpg, png, bmp) and Videos (mp4, avi, mov, mkv)"
        )
        
        if uploaded_file is not None:
            # Determine file type
            file_type = uploaded_file.type
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Check if it's an image or video
            is_image = file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'webp']
            is_video = file_extension in ['mp4', 'avi', 'mov', 'mkv', 'webm']
            
            if is_image:
                st.success(f"📸 Image uploaded: {uploaded_file.name}")
                
                # Read and display image
                file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if image is not None:
                    col_display, col_controls = st.columns([3, 1])
                    
                    with col_display:
                        st.image(image, channels="BGR", use_column_width=True)
                    
                    with col_controls:
                        st.caption(f"📐 Size: {image.shape[1]}x{image.shape[0]}")
                        
                        model_name = st.selectbox(
                            "Select Model:",
                            st.session_state.active_models,
                            key="image_model"
                        )
                        
                        if st.button("🔍 Detect Objects", type="primary"):
                            with st.spinner("Detecting objects..."):
                                result_img, detections = process_image(image, model_name)
                                st.image(result_img, channels="BGR", use_column_width=True)
                                
                                if detections:
                                    st.success(f"✅ Found {len(detections)} objects!")
                                    for det in detections:
                                        st.write(f"- {det.get('class_name', 'object')} ({det.get('confidence', 0):.2f})")
                                else:
                                    st.info("No objects detected")
            
            elif is_video:
                st.success(f"🎬 Video uploaded: {uploaded_file.name}")
                
                # Save video temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    video_path = tmp_file.name
                
                # Video controls
                col_vid1, col_vid2 = st.columns(2)
                with col_vid1:
                    model_name = st.selectbox(
                        "Select Model:",
                        st.session_state.active_models,
                        key="video_model"
                    )
                
                with col_vid2:
                    max_frames = st.slider(
                        "Max Frames to Process",
                        min_value=5,
                        max_value=100,
                        value=30,
                        step=5,
                        help="Process more frames for better analysis"
                    )
                
                # Video info
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()
                    
                    st.info(f"""
                    **Video Info:**
                    - 📐 Resolution: {width}x{height}
                    - ⏱️ FPS: {fps}
                    - 📄 Total Frames: {total_frames}
                    """)
                
                # Process video button
                if st.button("🚀 Process Video", type="primary"):
                    if st.session_state.processing:
                        st.warning("Processing already in progress...")
                    else:
                        st.session_state.processing = True
                        with st.spinner(f"Processing video with {model_name}..."):
                            processed_frames, detections_count = process_video_frames(
                                video_path, model_name, max_frames
                            )
                            
                            if processed_frames:
                                st.success(f"✅ Processed {len(processed_frames)} frames! Found {detections_count} objects total")
                                
                                # Show frame slider
                                st.markdown("---")
                                st.markdown("#### 📊 Frame Analysis")
                                
                                frame_index = st.slider(
                                    "Select Frame",
                                    min_value=0,
                                    max_value=len(processed_frames) - 1,
                                    value=0
                                )
                                
                                # Display selected frame
                                frame_data = processed_frames[frame_index]
                                frame_img = frame_data['frame']
                                frame_num = frame_data['number']
                                frame_detections = frame_data['detections']
                                
                                col_display, col_info = st.columns([2, 1])
                                
                                with col_display:
                                    st.image(frame_img, channels="BGR", use_column_width=True)
                                    st.caption(f"📸 Frame {frame_num + 1}/{len(processed_frames)}")
                                
                                with col_info:
                                    st.markdown("#### Detection Info")
                                    st.write(f"**Frame:** {frame_num + 1}")
                                    st.write(f"**Objects Found:** {len(frame_detections)}")
                                    
                                    if frame_detections:
                                        st.markdown("**Objects:**")
                                        for det in frame_detections[:10]:
                                            st.write(f"- {det.get('class_name', 'object')} ({det.get('confidence', 0):.2f})")
                                        if len(frame_detections) > 10:
                                            st.write(f"... and {len(frame_detections) - 10} more")
                                
                                # Summary stats
                                st.markdown("---")
                                st.markdown("#### 📊 Processing Summary")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Frames Processed", len(processed_frames))
                                with col2:
                                    st.metric("Total Detections", detections_count)
                                with col3:
                                    avg_detections = detections_count / len(processed_frames) if processed_frames else 0
                                    st.metric("Avg per Frame", f"{avg_detections:.1f}")
                                
                                # Download option
                                if st.button("📥 Download Processed Video"):
                                    st.info("Video download coming soon!")
                            else:
                                st.error("No frames processed. Please check the video file.")
                        
                        st.session_state.processing = False
                
                # Clean up temp file
                try:
                    os.unlink(video_path)
                except:
                    pass
            
            else:
                st.warning("⚠️ Unsupported file type. Please upload an image or video.")
        
        else:
            st.markdown("""
            <div class="upload-area">
                <div style="font-size: 3em;">📤</div>
                <p>Drag & drop or click to upload</p>
                <p style="color: #888; font-size: 0.8em;">Supports: Images (jpg, png) and Videos (mp4, avi, mov)</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Detection Stats")
        
        # Show stats
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Frames", st.session_state.frame_count)
        with col_info2:
            st.metric("Models", len(st.session_state.active_models) if st.session_state.models_loaded else 0)
        
        st.markdown("---")
        st.markdown("#### 🔧 Controls")
        
        if st.button("🔄 Reset"):
            st.session_state.processed_frames = []
            st.session_state.frame_count = 0
            st.session_state.detections = []
            st.rerun()
        
        if st.button("💾 Export Results"):
            st.info("Export feature coming soon!")
        
        st.markdown("---")
        st.markdown("#### 💡 Tips")
        st.markdown("""
        - Upload images for single detection
        - Upload videos for frame-by-frame analysis
        - Use slider to navigate video frames
        - Higher max frames = more detail but slower
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== WEBCAM ====================
elif st.session_state.page == "Webcam":
    st.markdown("### 📹 Webcam")
    st.info("Webcam feature coming soon!")

# ==================== MODELS ====================
elif st.session_state.page == "Models":
    st.markdown("### 🤖 Models")
    
    if not st.session_state.models_loaded:
        if st.button("🔄 Load Models", type="primary"):
            load_models()
            st.rerun()
        else:
            st.info("Click 'Load Models' to start")
    else:
        st.success(f"✅ {len(st.session_state.active_models)} models loaded")
        for model in st.session_state.active_models:
            st.write(f"- {model}")

# ==================== SETTINGS ====================
elif st.session_state.page == "Settings":
    st.markdown("### ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Configuration")
        st.slider("Detection Threshold", 0.1, 1.0, 0.5)
        st.slider("Confidence Score", 0.1, 1.0, 0.5)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Notifications")
        st.checkbox("Email Alerts")
        st.text_input("Alert Email", "admin@skyjames.ai")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("💾 Save Settings", type="primary"):
        notify("✅ Settings saved!")
        st.rerun()

# ==================== FOOTER ====================
st.markdown("""
<div style="text-align: center; color: #bbb; padding: 20px 0; border-top: 1px solid #e8e8e8; margin-top: 20px;">
    <p>🚀 SkyJames • Lane Detection • Image & Video Support</p>
</div>
""", unsafe_allow_html=True)
