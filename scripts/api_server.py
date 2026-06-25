"""
SkyJames - Production REST API Server
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
from pathlib import Path
import io

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.perception.object_detector import ObjectDetector
from src.safety.safety_monitor import SafetyMonitor
from src.config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize components
print("🚀 Initializing SkyJames API Server...")
config = Config()

# Load model if available
model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
if os.path.exists(model_path):
    print(f"✅ Loading model from: {model_path}")
else:
    print("⚠️ No trained model found, using traditional method")

detector = OptimizedLaneDetector(config, model_path=model_path if os.path.exists(model_path) else None)
object_detector = ObjectDetector(config)
safety_monitor = SafetyMonitor(config)

print("✅ API Server initialized successfully!")

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'service': 'SkyJames API',
        'version': '2.0.0',
        'status': 'running',
        'endpoints': {
            '/status': 'GET - Check API status',
            '/detect': 'POST - Detect lanes in image',
            '/detect_objects': 'POST - Detect objects in image',
            '/process_video': 'POST - Process video file',
            '/health': 'GET - Health check'
        }
    })

@app.route('/status', methods=['GET'])
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'model': 'lane_net_optimized.pth' if os.path.exists(model_path) else 'traditional',
        'device': 'cpu',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'lane_detection': 'available',
            'object_detection': 'available',
            'safety_monitor': 'available'
        }
    })

@app.route('/detect', methods=['POST'])
def detect_lanes():
    """Detect lanes in uploaded image"""
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read image
        img_bytes = file.read()
        img_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Process image
        result, left_lane, right_lane = detector.process_frame(img)
        
        # Encode result image
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

@app.route('/detect_objects', methods=['POST'])
def detect_objects():
    """Detect objects in uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img_bytes = file.read()
        img_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Detect objects
        detections = object_detector.detect_objects(img)
        result = object_detector.draw_detections(img, detections)
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', result)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'detections': detections,
            'count': len(detections),
            'image': result_base64,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_video', methods=['POST'])
def process_video():
    """Process video file"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No video selected'}), 400
        
        # Save temporary video
        temp_path = f"data/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        os.makedirs("data/temp", exist_ok=True)
        file.save(temp_path)
        
        # Process video (simplified - process first 30 frames for demo)
        cap = cv2.VideoCapture(temp_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = min(30, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        
        processed_frames = 0
        detections_count = 0
        
        for i in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            result, left, right = detector.process_frame(frame)
            processed_frames += 1
            if left is not None or right is not None:
                detections_count += 1
        
        cap.release()
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'status': 'success',
            'processed_frames': processed_frames,
            'total_frames': total_frames,
            'detections_made': detections_count,
            'fps': fps,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/safety_check', methods=['POST'])
def safety_check():
    """Check safety of detected objects"""
    try:
        data = request.get_json()
        if not data or 'detections' not in data:
            return jsonify({'error': 'No detections provided'}), 400
        
        # Check safety
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
            'violations': violations,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run on port 5001 to avoid conflict with MLflow
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
@app.route('/health/check', methods=['GET'])
def health_check():
    """Comprehensive health check"""
    checks = {
        'webcam': webcam.get_status() if 'webcam' in dir() else None,
        'mlflow': check_mlflow(),
        'models': check_models(),
        'database': check_database(),
        'disk': check_disk(),
    }
    return jsonify(checks)

# Add to existing api_server.py

from src.model_manager import load_all_models, model_manager

# Initialize models on startup
try:
    load_all_models()
    print("✅ All models loaded for API")
except Exception as e:
    print(f"⚠️ Error loading models: {e}")

@app.route('/api/models', methods=['GET'])
def list_models():
    """List all available models"""
    return jsonify({
        'active_models': model_manager.active_models,
        'models': list(model_manager.models.keys()),
        'device': str(model_manager.device)
    })

@app.route('/api/detect/<model_name>', methods=['POST'])
def detect_with_model(model_name):
    """Run detection with specific model"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img_array = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Run detection
        detections = model_manager.detect(img, model_name)
        drawn = model_manager.draw_detections(img, detections,
                                              model_manager.models[model_name]['type'])
        
        _, buffer = cv2.imencode('.jpg', drawn)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'model': model_name,
            'detections': detections,
            'count': len(detections) if detections else 0,
            'image': result_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/switch/<model_name>', methods=['POST'])
def switch_model(model_name):
    """Switch active model"""
    if model_name not in model_manager.models:
        return jsonify({'error': 'Model not found'}), 404
    
    # Update active models
    if model_name not in model_manager.active_models:
        model_manager.active_models.append(model_name)
    
    return jsonify({
        'status': 'success',
        'active_models': model_manager.active_models
    })
@app.route('/health/check', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'webcam': 'active' if st.session_state.webcam_running else 'inactive',
        'models': 'loaded' if st.session_state.models_loaded else 'not_loaded',
        'timestamp': datetime.now().isoformat()
    })
