import streamlit as st
import cv2
import numpy as np
import os
import sys
import time
from datetime import datetime
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="SkyJames", page_icon="🚀", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "Home"
if 'webcam_running' not in st.session_state: st.session_state.webcam_running = False
if 'models_loaded' not in st.session_state: st.session_state.models_loaded = False
if 'model_manager' not in st.session_state: st.session_state.model_manager = None
if 'active_models' not in st.session_state: st.session_state.active_models = []
if 'cap' not in st.session_state: st.session_state.cap = None
if 'captured_image' not in st.session_state: st.session_state.captured_image = None
if 'captured_detections' not in st.session_state: st.session_state.captured_detections = []
if 'video_count' not in st.session_state: st.session_state.video_count = 0
if 'notification' not in st.session_state: st.session_state.notification = ""
if 'frame_count' not in st.session_state: st.session_state.frame_count = 0
if 'processed_frames' not in st.session_state: st.session_state.processed_frames = []
if 'saved_captures' not in st.session_state: st.session_state.saved_captures = []
if 'capture_count' not in st.session_state: st.session_state.capture_count = 0

def go_home(): st.session_state.page = "Home"; st.rerun()
def notify(msg): st.session_state.notification = msg

def load_models():
    try:
        from src.model_manager_no_track import load_all_models
        manager = load_all_models()
        st.session_state.model_manager = manager
        st.session_state.active_models = manager.active_models
        st.session_state.models_loaded = True
        notify("✅ Models loaded!")
        return True
    except:
        notify("❌ Error loading models")
        return False

def start_webcam():
    try:
        if st.session_state.cap: st.session_state.cap.release()
        st.session_state.cap = cv2.VideoCapture(0)
        if not st.session_state.cap.isOpened(): st.session_state.cap = cv2.VideoCapture(1)
        if st.session_state.cap.isOpened():
            st.session_state.webcam_running = True
            notify("✅ Webcam started!")
            return True
        notify("❌ No camera")
        return False
    except:
        notify("❌ Camera error")
        return False

def stop_webcam():
    if st.session_state.cap: st.session_state.cap.release()
    st.session_state.cap = None
    st.session_state.webcam_running = False
    notify("⏹️ Webcam stopped")

def capture_and_save():
    if st.session_state.webcam_running and st.session_state.cap:
        ret, frame = st.session_state.cap.read()
        if ret:
            st.session_state.captured_image = frame.copy()
            st.session_state.captured_detections = []
            st.session_state.capture_count += 1
            os.makedirs("data/output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/output/capture_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            st.session_state.saved_captures.append(filename)
            notify(f"📸 Captured & Saved! ({st.session_state.capture_count})")
            return True
    notify("⚠️ Start webcam first")
    return False

def detect_captured(model_name):
    if st.session_state.captured_image is None:
        notify("⚠️ No captured image")
        return False
    if not st.session_state.models_loaded:
        notify("⚠️ Load models first")
        return False
    try:
        detections = st.session_state.model_manager.detect(st.session_state.captured_image, model_name)
        model_type = st.session_state.model_manager.models[model_name]['type']
        drawn = st.session_state.model_manager.draw_detections(st.session_state.captured_image.copy(), detections, model_type)
        st.session_state.captured_detections = detections
        st.session_state.captured_image = drawn
        notify(f"✅ Found {len(detections)} objects!")
        return True
    except:
        notify("❌ Detection error")
        return False

def process_video_frames(video_path, model_name, max_frames=30):
    if not st.session_state.models_loaded:
        notify("⚠️ Load models first")
        return [], 0
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            notify("❌ Could not open video")
            return [], 0
        frames = []
        total_detections = 0
        count = 0
        while cap.isOpened() and count < max_frames:
            ret, frame = cap.read()
            if not ret: break
            detections = st.session_state.model_manager.detect(frame, model_name)
            model_type = st.session_state.model_manager.models[model_name]['type']
            drawn = st.session_state.model_manager.draw_detections(frame.copy(), detections, model_type)
            frames.append({'frame': drawn, 'number': count, 'detections': detections, 'count': len(detections)})
            total_detections += len(detections)
            count += 1
        cap.release()
        st.session_state.frame_count = count
        st.session_state.processed_frames = frames
        notify(f"✅ Processed {count} frames!")
        return frames, total_detections
    except:
        notify("❌ Video error")
        return [], 0

def process_image_detection(image, model_name):
    if not st.session_state.models_loaded:
        notify("⚠️ Load models first")
        return image, []
    try:
        detections = st.session_state.model_manager.detect(image, model_name)
        model_type = st.session_state.model_manager.models[model_name]['type']
        drawn = st.session_state.model_manager.draw_detections(image.copy(), detections, model_type)
        return drawn, detections
    except:
        notify("❌ Detection error")
        return image, []

st.markdown('<style>.header{background:white;padding:20px;border-radius:10px;margin-bottom:20px;border:1px solid #ddd;}.header h1{margin:0;color:#1a1a2e;}.header h1 span{color:#4a6cf7;}.header p{color:#888;margin:5px 0 0 0;}.card{background:white;padding:20px;border-radius:10px;margin:10px 0;border:1px solid #ddd;}.metric{background:white;padding:15px;border-radius:10px;text-align:center;border:1px solid #ddd;}.metric .icon{font-size:2em;}.metric .value{font-size:1.5em;font-weight:bold;color:#1a1a2e;}.metric .label{color:#888;}.stButton>button{width:100% !important;border-radius:8px !important;font-weight:500 !important;}.stButton>button[kind="primary"]{background:#4a6cf7 !important;color:white !important;}.stButton>button[kind="secondary"]{background:#e8e8e8 !important;color:#1a1a2e !important;}.notification{padding:10px 15px;border-radius:8px;margin:10px 0;background:#e8f5e9;border-left:4px solid #34c759;}.notification.error{background:#fbe9e7;border-left-color:#ff3b30;}.upload-area{border:2px dashed #d0d0d0;padding:30px;border-radius:10px;text-align:center;}.upload-area:hover{border-color:#4a6cf7;background:#f8f9fa;}</style>', unsafe_allow_html=True)
st.markdown('<div class="header"><h1>🚀 SkyJames <span>Pipeline</span></h1><p>Webcam • Capture & Detect • Frame Analysis</p></div>', unsafe_allow_html=True)
if st.session_state.notification:
    cls = "notification"
    if "❌" in st.session_state.notification: cls += " error"
    st.markdown(f'<div class="{cls}">{st.session_state.notification}</div>', unsafe_allow_html=True)
    st.session_state.notification = ""

with st.sidebar:
    st.markdown("### 🚀 SkyJames")
    st.markdown("---")
    if st.button("🏠 Home", type="primary"): go_home()
    st.markdown("---")
    if st.button("📹 Webcam"): st.session_state.page = "Webcam"; st.rerun()
    if st.button("🛣️ Lane Detection"): st.session_state.page = "Lane"; st.rerun()
    if st.button("🤖 Models"): st.session_state.page = "Models"; st.rerun()
    if st.button("⚙️ Settings"): st.session_state.page = "Settings"; st.rerun()
    st.markdown("---")
    st.markdown(f"**Webcam:** {'✅' if st.session_state.webcam_running else '⏸️'}")
    st.markdown(f"**Models:** {'✅' if st.session_state.models_loaded else '❌'}")
    st.markdown(f"**Captures:** {st.session_state.capture_count}")
    st.markdown(f"**Frames:** {st.session_state.frame_count}")

if st.session_state.page == "Home":
    st.markdown("### Dashboard Overview")
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric"><div class="icon">📹</div><div class="value">{"✅" if st.session_state.webcam_running else "⏸️"}</div><div class="label">Webcam</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric"><div class="icon">🤖</div><div class="value">{len(st.session_state.active_models) if st.session_state.models_loaded else 0}</div><div class="label">Models</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric"><div class="icon">📸</div><div class="value">{st.session_state.capture_count}</div><div class="label">Captures</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric"><div class="icon">📊</div><div class="value">{st.session_state.frame_count}</div><div class="label">Frames</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("📹 Open Webcam", type="primary"): st.session_state.page = "Webcam"; st.rerun()
    with c2:
        if st.button("🤖 Load Models", type="primary"): load_models(); st.rerun()
    with c3:
        if st.button("🛣️ Lane Detection", type="primary"): st.session_state.page = "Lane"; st.rerun()

elif st.session_state.page == "Webcam":
    st.markdown("### 📹 Webcam - Capture, Save & Detect")
    if st.button("🏠 Home", type="secondary"): go_home()
    if not st.session_state.models_loaded:
        st.warning("⚠️ Load models for detection")
        if st.button("Load Models", type="primary"): load_models(); st.rerun()
    c1,c2 = st.columns([2,1])
    with c1:
        st.markdown('<div class="card"><h4>📷 Live Feed</h4>', unsafe_allow_html=True)
        col1,col2,col3 = st.columns(3)
        with col1:
            if not st.session_state.webcam_running:
                if st.button("▶️ Start", type="primary"): start_webcam(); st.rerun()
            else:
                if st.button("⏹️ Stop", type="secondary"): stop_webcam(); st.rerun()
        with col2:
            if st.button("📸 Capture & Save", type="primary"): capture_and_save(); st.rerun()
        with col3:
            if st.button("🔄 Refresh"): st.rerun()
        if st.session_state.webcam_running and st.session_state.cap:
            ret, frame = st.session_state.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, channels="RGB", use_column_width=True)
                st.caption("📹 Live - Camera is active")
                time.sleep(0.05); st.rerun()
            else: st.warning("Waiting for frames...")
        else: st.info("Click 'Start' to begin")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.captured_image is not None:
            st.markdown('<div class="card"><h4>📸 Captured Image</h4>', unsafe_allow_html=True)
            col_cap, col_info = st.columns([2,1])
            with col_cap:
                img_rgb = cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB)
                st.image(img_rgb, channels="RGB", use_column_width=True)
                if st.session_state.models_loaded and st.session_state.active_models:
                    model_name = st.selectbox("Select Model:", st.session_state.active_models, key="cap_model")
                    if st.button("🔍 Detect Objects", type="primary"): detect_captured(model_name); st.rerun()
            with col_info:
                st.markdown("#### Detection Results")
                if st.session_state.captured_detections:
                    st.success(f"✅ Found {len(st.session_state.captured_detections)} objects!")
                    for det in st.session_state.captured_detections[:10]: st.write(f"- {det.get('class_name', 'object')} ({det.get('confidence', 0):.2f})")
                else: st.info("No detections yet")
                if st.button("🗑️ Clear Captured"): st.session_state.captured_image = None; st.session_state.captured_detections = []; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h4>📊 Capture History</h4>', unsafe_allow_html=True)
        if st.session_state.saved_captures:
            st.write(f"**Total Captures:** {len(st.session_state.saved_captures)}")
            for i, path in enumerate(st.session_state.saved_captures[-5:]): st.write(f"{i+1}. {os.path.basename(path)}")
            if st.button("🗑️ Clear History"): st.session_state.saved_captures = []; st.rerun()
        else: st.info("No captures yet")
        st.markdown("---")
        st.markdown("#### 💡 How to Use")
        st.markdown("1. Click **Start** to begin webcam\n2. Click **Capture & Save** to capture frame\n3. Select a model\n4. Click **Detect Objects** to analyze\n5. Results show detected objects")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Lane":
    st.markdown("### 🛣️ Lane Detection - Images & Videos")
    if st.button("🏠 Home", type="secondary"): go_home()
    if not st.session_state.models_loaded:
        st.warning("⚠️ Load models first")
        if st.button("Load Models", type="primary"): load_models(); st.rerun()
        st.stop()
    st.success(f"✅ {len(st.session_state.active_models)} models ready")
    c1,c2 = st.columns([2,1])
    with c1:
        st.markdown('<div class="card"><h4>📤 Upload Image or Video</h4>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose image or video...", type=['jpg','png','jpeg','bmp','mp4','avi','mov','mkv'])
        if uploaded is not None:
            file_ext = uploaded.name.split('.')[-1].lower()
            is_image = file_ext in ['jpg','jpeg','png','bmp']
            is_video = file_ext in ['mp4','avi','mov','mkv']
            if is_image:
                st.success(f"📸 Image: {uploaded.name}")
                bytes_data = np.frombuffer(uploaded.read(), np.uint8)
                image = cv2.imdecode(bytes_data, cv2.IMREAD_COLOR)
                if image is not None:
                    st.image(image, channels="BGR", use_column_width=True)
                    model = st.selectbox("Model:", st.session_state.active_models, key="img_model")
                    if st.button("🔍 Detect Objects", type="primary"):
                        with st.spinner("Detecting..."):
                            drawn, detections = process_image_detection(image, model)
                            st.image(drawn, channels="BGR", use_column_width=True)
                            if detections:
                                st.success(f"✅ Found {len(detections)} objects!")
                                for d in detections[:10]: st.write(f"- {d.get('class_name', 'object')} ({d.get('confidence', 0):.2f})")
                            else: st.info("No objects detected")
            elif is_video:
                st.success(f"🎬 Video: {uploaded.name}")
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
                    tmp.write(uploaded.read()); video_path = tmp.name
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    fps = int(cap.get(cv2.CAP_PROP_FPS)); total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()
                    st.info(f"📐 {width}x{height} | ⏱️ {fps} FPS | 📄 {total} frames")
                model = st.selectbox("Model:", st.session_state.active_models, key="vid_model")
                max_frames = st.slider("Max Frames", 5, 100, 30, 5)
                if st.button("🚀 Process Video", type="primary"):
                    with st.spinner("Processing..."):
                        frames, total_dets = process_video_frames(video_path, model, max_frames)
                        if frames:
                            st.success(f"✅ Processed {len(frames)} frames, {total_dets} objects!")
                            frame_idx = st.slider("Select Frame", 0, len(frames)-1, 0)
                            frame_data = frames[frame_idx]
                            col_img, col_info = st.columns([2,1])
                            with col_img:
                                st.image(frame_data['frame'], channels="BGR", use_column_width=True)
                                st.caption(f"Frame {frame_idx + 1}/{len(frames)}")
                            with col_info:
                                st.write(f"**Objects:** {len(frame_data['detections'])}")
                                for d in frame_data['detections'][:5]: st.write(f"- {d.get('class_name', 'object')} ({d.get('confidence', 0):.2f})")
                            c1,c2,c3 = st.columns(3)
                            c1.metric("Frames", len(frames)); c2.metric("Detections", total_dets); c3.metric("Avg", f"{total_dets/len(frames):.1f}")
                try: os.unlink(video_path)
                except: pass
            else: st.warning("Unsupported file type")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h4>📊 Stats</h4>', unsafe_allow_html=True)
        st.metric("Frames Processed", st.session_state.frame_count)
        st.metric("Models", len(st.session_state.active_models))
        if st.button("🔄 Reset"): st.session_state.processed_frames = []; st.session_state.frame_count = 0; st.rerun()
        st.markdown("---")
        st.markdown("#### 💡 Tips")
        st.markdown("- Upload images for single detection\n- Upload videos for frame analysis\n- Use slider to browse frames")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Models":
    st.markdown("### 🤖 Models")
    if st.button("🏠 Home", type="secondary"): go_home()
    if not st.session_state.models_loaded:
        if st.button("Load Models", type="primary"): load_models(); st.rerun()
        else: st.info("Click 'Load Models' to start")
    else:
        st.success(f"✅ {len(st.session_state.active_models)} models loaded")
        for m in st.session_state.active_models: st.write(f"- {m}")
        if st.button("Reload Models"): st.session_state.models_loaded = False; st.rerun()

elif st.session_state.page == "Settings":
    st.markdown("### ⚙️ Settings")
    if st.button("🏠 Home", type="secondary"): go_home()
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><h4>Configuration</h4>', unsafe_allow_html=True)
        st.slider("Detection Threshold", 0.1, 1.0, 0.5)
        st.slider("Confidence Score", 0.1, 1.0, 0.5)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h4>Notifications</h4>', unsafe_allow_html=True)
        st.checkbox("Email Alerts")
        st.text_input("Alert Email", "admin@skyjames.ai")
        st.markdown('</div>', unsafe_allow_html=True)
    if st.button("💾 Save Settings", type="primary"): notify("✅ Settings saved!"); st.rerun()

st.markdown('<div style="text-align:center;color:#999;padding:20px 0;margin-top:20px;border-top:1px solid #ddd;"><p>🚀 SkyJames • Webcam Capture & Detect • Frame Analysis</p></div>', unsafe_allow_html=True)
