"""
SkyJames - Simple Webcam Server
Run with: python webcam_simple.py
"""

import cv2
import time
import threading
from flask import Flask, Response, render_template_string, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import detector, but fallback if not available
try:
    from src.perception.lane_net_cpu import OptimizedLaneDetector
    from src.config import Config
    detector = OptimizedLaneDetector(Config())
    has_detector = True
except:
    has_detector = False
    print("⚠️ Lane detector not available - showing raw webcam")

app = Flask(__name__)

# Global variables
camera = None
current_frame = None
frame_lock = threading.Lock()
is_running = False

def capture_frames():
    global camera, current_frame, is_running
    
    print("📷 Opening webcam...")
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        # Try alternative camera IDs
        for alt_id in [1, 2, -1]:
            camera = cv2.VideoCapture(alt_id)
            if camera.isOpened():
                break
    
    if not camera.isOpened():
        print("❌ Could not open webcam")
        return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    is_running = True
    print("✅ Webcam capture started")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process with detector if available
        if has_detector:
            try:
                result, left, right = detector.process_frame(frame)
                frame_to_show = result
            except:
                frame_to_show = frame
        else:
            frame_to_show = frame
        
        # Add overlay
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        cv2.putText(frame_to_show, f"SkyJames AI - FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame_to_show, f"Frames: {frame_count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        with frame_lock:
            _, buffer = cv2.imencode('.jpg', frame_to_show)
            current_frame = buffer.tobytes()

def generate_frames():
    while True:
        with frame_lock:
            if current_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
        time.sleep(0.03)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SkyJames Webcam</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #0a0a1a; 
                color: white; 
                text-align: center; 
                padding: 20px;
                margin: 0;
            }
            h1 { color: #4a6cf7; }
            .video-container {
                background: #1a1a2e;
                border-radius: 16px;
                padding: 10px;
                margin: 20px auto;
                max-width: 800px;
                border: 2px solid #4a6cf7;
            }
            img { width: 100%; border-radius: 10px; }
            .status {
                background: #1a1a2e;
                padding: 15px;
                border-radius: 10px;
                margin: 10px auto;
                max-width: 800px;
            }
            .online { color: #34c759; }
            .info { color: #888; font-size: 0.9em; }
            a { color: #4a6cf7; text-decoration: none; }
            .controls {
                display: flex;
                gap: 10px;
                justify-content: center;
                flex-wrap: wrap;
                margin: 20px 0;
            }
            button {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                background: #4a6cf7;
                color: white;
            }
            button:hover {
                background: #3a5cd7;
                transform: scale(1.05);
            }
            button.stop {
                background: #ff3b30;
            }
            button.stop:hover {
                background: #e6352a;
            }
        </style>
    </head>
    <body>
        <h1>📹 SkyJames Webcam</h1>
        <p style="color: #888;">Real-time Lane Detection</p>
        
        <div class="video-container">
            <img src="/video_feed" id="stream" alt="Webcam Stream">
        </div>
        
        <div class="controls">
            <button onclick="refreshStream()">🔄 Refresh</button>
            <button onclick="toggleFullscreen()">⛶ Fullscreen</button>
        </div>
        
        <div class="status">
            <span class="online">✅ Live Stream Active</span>
            <br>
            <span class="info">📱 Mobile: Open this page on your phone</span>
            <br>
            <span class="info">🔗 <a href="/video_feed">Direct Stream URL</a></span>
        </div>
        
        <script>
            function refreshStream() {
                const img = document.getElementById('stream');
                img.src = '/video_feed?t=' + Date.now();
            }
            
            function toggleFullscreen() {
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    }
                }
            }
            
            // Auto-refresh
            setInterval(refreshStream, 100);
        </script>
    </body>
    </html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify({
        'status': 'running' if is_running else 'stopped',
        'detector': 'active' if has_detector else 'inactive'
    })

if __name__ == '__main__':
    # Start capture thread
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()
    
    # Give camera time to initialize
    time.sleep(2)
    
    print("=" * 50)
    print("📹 SkyJames Webcam Server")
    print("=" * 50)
    print("")
    print("📊 Access URLs:")
    print("  - http://localhost:5004")
    print("  - http://127.0.0.1:5004")
    print("")
    print("📱 On mobile, use your IP:")
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print(f"  - http://{ip}:5004")
    except:
        print("  - (IP detection failed, use localhost)")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5004, debug=False, threaded=True)
