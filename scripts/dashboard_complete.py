"""
SkyJames - Complete Dashboard
Webcam with Capture & Detection + Lane Detection (Image & Video)
"""

import streamlit as st
import cv2
import numpy as np
import os
import sys
import time
import tempfile
from PIL import Image
import io
import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page config
st.set_page_config(
    page_title="SkyJames",
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
if 'cap' not in st.session_state:
    st.session_state.cap = None
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'captured_image' not in st.session_state:
    st.session_state.captured_image = None
if 'captured_detections' not in st.session_state:
    st.session_state.captured_detections = []
if 'processed_frames' not in st.session_state:
    st.session_state.processed_frames = []
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'capture_count' not in st.session_state:
    st.session_state.capture_count = 0
if 'saved_images' not in st.session_state:
    st.session_state.saved_images = []

# ==================== HELPER FUNCTIONS ====================
def notify(msg):
    st.session_state.notification = msg

def start_webcam():
    try:
        if st.session_state.cap is not None:
            st.session_state.cap.release()
        
        st.session_state.cap = cv2.VideoCapture(0)
        if not st.session_state.cap.isOpened():
            st.session_state.cap = cv2.VideoCapture(1)
        
        if st.session_state.cap.isOpened():
            st.session_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            st.session_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            st.session_state.webcam_running = True
            notify("✅ Webcam started!")
            return True
        else:
            notify("❌ Could not access webcam")
            return False
    except Exception as e:
        notify(f"❌ Webcam error: {e}")
        return False

def stop_webcam():
    if st.session_state.cap:
        st.session_state.cap.release()
        st.session_state.cap = None
    st.session_state.webcam_running = False
    st.session_state.frame = None
    notify("⏹️ Webcam stopped")

def get_frame():
    if st.session_state.webcam_running and st.session_state.cap:
        ret, frame = st.session_state.cap.read()
        if ret:
            st.session_state.frame = frame
            return frame
    return None

def capture_and_save():
    """Capture current frame, save it, and prepare for detection"""
    if st.session_state.webcam_running and st.session_state.cap:
        ret, frame = st.session_state.cap.read()
        if ret:
            # Save to session state
            st.session_state.captured_image = frame.copy()
            st.session_state.captured_detections = []
            st.session_state.capture_count += 1
            
            # Save to file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/output/capture_{timestamp}.jpg"
            os.makedirs("data/output", exist_ok=True)
            cv2.imwrite(filename, frame)
            st.session_state.saved_images.append(filename)
            
            notify(f"📸 Frame captured and saved! ({st.session_state.capture_count})")
            return True
    notify("⚠️ Start webcam first")
    return False

def detect_captured_image(model_name):
    """Run detection on captured image"""
    if st.session_state.captured_image is not None:
        try:
            model_manager = st.session_state.model_manager
            detections = model_manager.detect(st.session_state.captured_image, model_name)
            model_type = model_manager.models[model_name]['type']
            drawn = model_manager.draw_detections(st.session_state.captured_image.copy(), detections, model_type)
            st.session_state.captured_detections = detections
            st.session_state.captured_image = drawn
            notify(f"✅ Found {len(detections)} objects!")
            return True
        except Exception as e:
            notify(f"❌ Detection error: {e}")
            return False
    notify("⚠️ No captured image")
    return False

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
            
            detections = model_manager.detect(frame, model_name)
            model_type = model_manager.models[model_name]['type']
            drawn = model_manager.draw_detections(frame.copy(), detections, model_type)
            
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
    .webcam-container {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 10px;
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .webcam-container img {
        width: 100%;
        border-radius: 8px;
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
    .captured-container {
        border: 2px solid #4a6cf7;
        border-radius: 10px;
        padding: 10px;
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="header">
    <h1>🚀 SkyJames <span>Pipeline</span></h1>
    <p>Webcam • Capture & Detect • Lane Detection</p>
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
    st.markdown(f"**Captures:** {st.session_state.capture_count}")
    webcam_status = "✅ Active" if st.session_state.webcam_running else "⏸️ Stopped"
    st.markdown(f"**Webcam:** {webcam_status}")
    models_status = "✅ Loaded" if st.session_state.models_loaded else "❌ Not Loaded"
    st.markdown(f"**Models:** {models_status}")
    st.markdown(f"**Frames:** {st.session_state.frame_count}")

# ==================== HOME ====================
if st.session_state.page == "Home":
    st.markdown("### Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric">
            <div class="icon">🛣️</div>
            <div class="value">Active</div>
            <div class="label">Lane Detection</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status = "✅" if st.session_state.webcam_running else "⏸️"
        st.markdown(f"""
        <div class="metric">
            <div class="icon">📹</div>
            <div class="value">{status}</div>
            <div class="label">Webcam</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric">
            <div class="icon">📸</div>
            <div class="value">{st.session_state.capture_count}</div>
            <div class="label">Captures</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric">
            <div class="icon">🤖</div>
            <div class="value">{len(st.session_state.active_models) if st.session_state.models_loaded else 0}</div>
            <div class="label">Models</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📹 Open Webcam", type="primary"):
            st.session_state.page = "Webcam"
            st.rerun()
    with col2:
        if st.button("🛣️ Open Lane Detection", type="primary"):
            st.session_state.page = "Lane"
            st.rerun()
    with col3:
        if st.button("🤖 Load Models", type="primary"):
            load_models()
            st.rerun()

# ==================== WEBCAM ====================
elif st.session_state.page == "Webcam":
    st.markdown("### 📹 Webcam - Capture & Detect")
    st.caption("Start webcam, capture frames, and detect objects")
    
    if not st.session_state.models_loaded:
        st.warning("⚠️ Models not loaded. Load them first for detection.")
        if st.button("🔄 Load Models", type="primary"):
            load_models()
            st.rerun()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📷 Live Feed")
        
        # Webcam controls
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if not st.session_state.webcam_running:
                if st.button("▶️ Start", type="primary"):
                    if start_webcam():
                        st.rerun()
            else:
                if st.button("⏹️ Stop", type="secondary"):
                    stop_webcam()
                    st.rerun()
        
        with col_btn2:
            if st.button("📸 Capture & Save", type="primary"):
                if capture_and_save():
                    st.rerun()
        
        with col_btn3:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Live feed display
        if st.session_state.webcam_running:
            frame = get_frame()
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, channels="RGB", use_column_width=True)
                st.caption("📹 Live - Camera is active")
                time.sleep(0.03)
                st.rerun()
            else:
                st.warning("Waiting for frames...")
                time.sleep(0.1)
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 40px; background: #f8f9fa; border-radius: 8px;">
                <div style="font-size: 3em;">📹</div>
                <p style="color: #888;">Click <strong>Start</strong> to begin</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Captured image with detection
        if st.session_state.captured_image is not None:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 📸 Captured Image")
            
            col_cap, col_info = st.columns([2, 1])
            
            with col_cap:
                # Display captured image
                img_rgb = cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB)
                st.image(img_rgb, channels="RGB", use_column_width=True)
                
                # Detection controls for captured image
                if st.session_state.models_loaded:
                    model_name = st.selectbox(
                        "Select Model for Detection:",
                        st.session_state.active_models,
                        key="capture_model"
                    )
                    
                    if st.button("🔍 Detect Objects", type="primary"):
                        if detect_captured_image(model_name):
                            st.rerun()
            
            with col_info:
                st.markdown("#### Detection Results")
                if st.session_state.captured_detections:
                    st.success(f"✅ Found {len(st.session_state.captured_detections)} objects!")
                    for det in st.session_state.captured_detections:
                        st.write(f"- {det.get('class_name', 'object')} ({det.get('confidence', 0):.2f})")
                else:
                    st.info("No detections yet. Click 'Detect Objects'")
                
                if st.button("🗑️ Clear Captured"):
                    st.session_state.captured_image = None
                    st.session_state.captured_detections = []
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Capture History")
        
        if st.session_state.saved_images:
            st.write(f"**Total Captures:** {len(st.session_state.saved_images)}")
            for i, img_path in enumerate(st.session_state.saved_images[-5:]):
                st.write(f"{i+1}. {os.path.basename(img_path)}")
            
            if st.button("🗑️ Clear History"):
                st.session_state.saved_images = []
                st.rerun()
        else:
            st.info("No captures yet")
        
        st.markdown("---")
        st.markdown("#### 💡 How to Use")
        st.markdown("""
        1. Click **Start** to begin webcam
        2. Click **Capture & Save** to capture frame
        3. Select a model
        4. Click **Detect Objects** to analyze
        5. Results show detected objects
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== LANE DETECTION ====================
elif st.session_state.page == "Lane":
    st.markdown("### 🛣️ Lane Detection")
    st.caption("Upload images or videos for object detection")
    
    if not st.session_state.models_loaded:
        st.warning("⚠️ Models not loaded.")
        if st.button("🔄 Load Models", type="primary"):
            load_models()
            st.rerun()
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📤 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose an image or video...",
            type=['jpg', 'jpeg', 'png', 'bmp', 'mp4', 'avi', 'mov', 'mkv'],
            help="Images: jpg, png, bmp | Videos: mp4, avi, mov, mkv"
        )
        
        if uploaded_file is not None:
            file_ext = uploaded_file.name.split('.')[-1].lower()
            is_image = file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']
            is_video = file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm']
            
            if is_image:
                st.success(f"📸 Image: {uploaded_file.name}")
                file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if image is not None:
                    st.image(image, channels="BGR", use_column_width=True)
                    
                    model_name = st.selectbox("Select Model:", st.session_state.active_models, key="img_model")
                    
                    if st.button("🔍 Detect Objects", type="primary"):
                        with st.spinner("Detecting..."):
                            result_img, detections = process_image(image, model_name)
                            st.image(result_img, channels="BGR", use_column_width=True)
                            
                            if detections:
                                st.success(f"✅ Found {len(detections)} objects!")
                                for det in detections:
                                    st.write(f"- {det.get('class_name', 'object')} ({det.get('confidence', 0):.2f})")
                            else:
                                st.info("No objects detected")
            
            elif is_video:
                st.success(f"🎬 Video: {uploaded_file.name}")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    video_path = tmp_file.name
                
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()
                    
                    st.info(f"📐 {width}x{height} | ⏱️ {fps} FPS | 📄 {total_frames} frames")
                
                model_name = st.selectbox("Select Model:", st.session_state.active_models, key="vid_model")
                max_frames = st.slider("Max Frames", 5, 100, 30, 5)
                
                if st.button("🚀 Process Video", type="primary"):
                    with st.spinner("Processing..."):
                        processed_frames, detections_count = process_video_frames(video_path, model_name, max_frames)
                        
                        if processed_frames:
                            st.success(f"✅ Processed {len(processed_frames)} frames! {detections_count} objects found")
                            
                            frame_idx = st.slider("Frame", 0, len(processed_frames)-1, 0)
                            frame_data = processed_frames[frame_idx]
                            
                            col_img, col_info = st.columns([2, 1])
                            with col_img:
                                st.image(frame_data['frame'], channels="BGR", use_column_width=True)
                                st.caption(f"Frame {frame_idx + 1}/{len(processed_frames)}")
                            with col_info:
                                st.write(f"**Objects:** {len(frame_data['detections'])}")
                                for det in frame_data['detections'][:5]:
                                    st.write(f"- {det.get('class_name', 'object')} ({det.get('confidence', 0):.2f})")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Frames", len(processed_frames))
                            with col2:
                                st.metric("Detections", detections_count)
                            with col3:
                                st.metric("Avg", f"{detections_count/len(processed_frames):.1f}")
                
                try:
                    os.unlink(video_path)
                except:
                    pass
            
            else:
                st.warning("Unsupported file type")
        
        else:
            st.markdown("""
            <div class="upload-area">
                <div style="font-size: 3em;">📤</div>
                <p>Drop files here or click to upload</p>
                <p style="color: #888; font-size: 0.8em;">Images: jpg, png, bmp • Videos: mp4, avi, mov</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Stats")
        st.metric("Frames", st.session_state.frame_count)
        st.metric("Models", len(st.session_state.active_models) if st.session_state.models_loaded else 0)
        
        if st.button("🔄 Reset"):
            st.session_state.processed_frames = []
            st.session_state.frame_count = 0
            st.rerun()
        
        st.markdown("---")
        st.markdown("#### 💡 Tips")
        st.markdown("- Upload images for single detection")
        st.markdown("- Upload videos for frame analysis")
        st.markdown("- Use slider to browse frames")
        
        st.markdown('</div>', unsafe_allow_html=True)

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
        st.text_input("Email", "admin@skyjames.ai")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("💾 Save Settings", type="primary"):
        notify("✅ Settings saved!")
        st.rerun()

# ==================== FOOTER ====================
st.markdown("""
<div style="text-align: center; color: #bbb; padding: 20px 0; border-top: 1px solid #e8e8e8; margin-top: 20px;">
    <p>🚀 SkyJames • Webcam Capture & Detect • Lane Detection</p>
</div>
""", unsafe_allow_html=True)
