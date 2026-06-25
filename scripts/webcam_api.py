
"""
SkyJames - Webcam API Endpoint
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import base64
import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.webcam_capture import webcam

app = Flask(__name__)
CORS(app)

@app.route('/webcam/start', methods=['POST'])
def start_webcam():
    data = request.get_json() or {}
    camera_id = data.get('camera_id', 0)
    result = webcam.start_camera(camera_id)
    return jsonify(result)

@app.route('/webcam/stop', methods=['POST'])
def stop_webcam():
    result = webcam.stop_camera()
    return jsonify(result)

@app.route('/webcam/frame', methods=['GET'])
def get_frame():
    frame_base64 = webcam.get_frame_base64()
    if frame_base64:
        return jsonify({
            'status': 'success',
            'image': frame_base64,
            'timestamp': datetime.now().isoformat()
        })
    return jsonify({'status': 'error', 'message': 'No frame available'})

@app.route('/webcam/status', methods=['GET'])
def get_status():
    status = webcam.get_status()
    return jsonify(status)

@app.route('/webcam/record', methods=['POST'])
def record_video():
    data = request.get_json() or {}
    duration = data.get('duration', 10)
    result = webcam.save_video(duration)
    return jsonify(result)

@app.route('/webcam/stream')
def stream():
    def generate():
        while True:
            frame = webcam.get_frame()
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
