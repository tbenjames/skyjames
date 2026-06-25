"""
SkyJames - Webcam Server (Flask)
Accessible from any browser
Run with: python webcam_server.py
"""

from flask import Flask, Response, render_template_string, jsonify
import cv2
import numpy as np
import time
import threading
import socket
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

app = Flask(__name__)

# Global variables
camera = None
detector = OptimizedLaneDetector(Config())
frame_lock = threading.Lock()
current_frame = None
frame_count = 0
fps = 0
start_time = time.time()
is_running = False

def capture_frames():
    global camera, current_frame, frame_count, fps, start_time, is_running
    
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Could not open webcam")
        return
    
    is_running = True
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Webcam capture started")
    
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        
        # Process frame
        result, left, right = detector.process_frame(frame)
        
        # Calculate FPS
        frame_count += 1
        elapsed = time.time() - start_time
        if elapsed > 0:
            fps = frame_count / elapsed
        
        # Add overlay
        cv2.putText(result, f"SkyJames AI - FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        lane_status = "BOTH" if (left is not None and right is not None) else \
                     "LEFT" if left is not None else \
                     "RIGHT" if right is not None else "NONE"
        cv2.putText(result, f"Lanes: {lane_status}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(result, f"Frames: {frame_count}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        with frame_lock:
            _, buffer = cv2.imencode('.jpg', result)
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
            h1 { 
                color: #4a6cf7; 
                font-size: 2em;
                margin-bottom: 10px;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
            }
            .video-container {
                background: #1a1a2e;
                border-radius: 16px;
                padding: 10px;
                margin: 20px 0;
                border: 2px solid #4a6cf7;
            }
            img { 
                width: 100%; 
                border-radius: 10px;
                display: block;
            }
            .status {
                background: #1a1a2e;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
            }
            .online { color: #34c759; }
            a { color: #4a6cf7; text-decoration: none; }
            .info {
                color: #888;
                font-size: 0.9em;
                margin: 5px 0;
            }
            @media (max-width: 600px) {
                h1 { font-size: 1.5em; }
                .video-container { padding: 5px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📹 SkyJames Webcam</h1>
            <p style="color: #888;">Real-time Lane Detection</p>
            <div class="video-container">
                <img src="/video_feed" id="stream" alt="Webcam Stream">
            </div>
            <div class="status">
                <span class="online">✅ Live Stream Active</span>
                <br>
                <span class="info">Press 'q' in terminal to quit</span>
                <br>
                <span class="info">📱 Mobile: Open this page on your phone</span>
                <br>
                <span class="info">🔗 <a href="/video_feed">Direct Stream URL</a></span>
            </div>
        </div>
        <script>
            // Auto-refresh stream
            setInterval(() => {
                const img = document.getElementById('stream');
                img.src = '/video_feed?t=' + Date.now();
            }, 100);
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
        'fps': round(fps, 1),
        'frames': frame_count,
        'webcam': 'active' if camera and camera.isOpened() else 'inactive'
    })

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    # Start capture thread
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()
    
    # Give camera time to initialize
    time.sleep(2)
    
    # Get IP address
    ip_address = get_local_ip()
    
    print("=" * 50)
    print("📹 SkyJames Webcam Server")
    print("=" * 50)
    print("✅ Webcam started!")
    print("")
    print("📊 Access URLs:")
    print(f"  - Local: http://localhost:5004")
    print(f"  - IP: http://{ip_address}:5004")
    print(f"  - Video Stream: http://localhost:5004/video_feed")
    print(f"  - Status: http://localhost:5004/status")
    print("")
    print("📱 On mobile, use your IP:")
    print(f"  - http://{ip_address}:5004")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5004, debug=False, threaded=True)
