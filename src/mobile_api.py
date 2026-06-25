"""
SkyJames - Mobile App Backend API
Optimized for mobile app integration (React Native/Flutter)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import sys
import json
import base64
from datetime import datetime
import io
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.perception.object_detector import ObjectDetector
from src.safety.safety_monitor import SafetyMonitor
from src.config import Config

app = Flask(__name__)
CORS(app)

config = Config()
detector = OptimizedLaneDetector(config)
object_detector = ObjectDetector(config)
safety_monitor = SafetyMonitor(config)

@app.route('/api/mobile/status', methods=['GET'])
def mobile_status():
    """Mobile app status endpoint"""
    return jsonify({
        'status': 'online',
        'version': '2.0.0',
        'model': 'lane_net_optimized.pth',
        'features': ['lane_detection', 'object_detection', 'safety_monitor']
    })

@app.route('/api/mobile/detect', methods=['POST'])
def mobile_detect():
    """Mobile-optimized detection endpoint"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Process
        result, left_lane, right_lane = detector.process_frame(img)
        
        # Encode result to base64
        _, buffer = cv2.imencode('.jpg', result)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'left_lane': left_lane,
            'right_lane': right_lane,
            'image': result_base64,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/objects', methods=['POST'])
def mobile_objects():
    """Mobile-optimized object detection"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        image_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        detections = object_detector.detect_objects(img)
        result = object_detector.draw_detections(img, detections)
        
        _, buffer = cv2.imencode('.jpg', result)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'detections': detections,
            'count': len(detections),
            'image': result_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/safety', methods=['POST'])
def mobile_safety():
    """Mobile safety check"""
    try:
        data = request.get_json()
        if not data or 'detections' not in data:
            return jsonify({'error': 'No detections provided'}), 400
        
        perception_result = {'detections': data['detections'], 'lane_lines': (None, None)}
        is_safe, violations = safety_monitor.evaluate_safety(
            perception_result, 
            {'predicted_path': None},
            {'control': None},
            None
        )
        
        return jsonify({
            'status': 'success',
            'safe': is_safe,
            'violations': violations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
