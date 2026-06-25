
"""
SkyJames - Universal Webcam Capture
Works on Desktop (PC/Mac) and Mobile (iOS/Android)
"""

import cv2
import base64
import json
import time
import threading
import queue
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

class WebcamCapture:
    def __init__(self):
        self.camera = None
        self.is_capturing = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.thread = None
        self.last_frame = None
        self.detector = OptimizedLaneDetector(Config())
        self.fps = 0
        self.frame_count = 0
        self.start_time = None
    
    def start_camera(self, camera_id=0):
        try:
            self.camera = cv2.VideoCapture(camera_id)
            if not self.camera.isOpened():
                for alt_id in [1, 2, -1]:
                    self.camera = cv2.VideoCapture(alt_id)
                    if self.camera.isOpened():
                        break
            
            if not self.camera.isOpened():
                return {'error': 'No camera detected'}
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_capturing = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            return {'status': 'success', 'message': 'Camera started'}
        except Exception as e:
            return {'error': str(e)}
    
    def _capture_loop(self):
        while self.is_capturing:
            if self.camera is None or not self.camera.isOpened():
                break
            
            ret, frame = self.camera.read()
            if not ret:
                break
            
            self.frame_count += 1
            
            if self.start_time:
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.fps = self.frame_count / elapsed
            
            processed_frame, left, right = self.detector.process_frame(frame)
            self.last_frame = processed_frame
            
            cv2.putText(processed_frame, f"FPS: {self.fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(processed_frame, f"Frames: {self.frame_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            lane_status = "BOTH" if (left is not None and right is not None) else                          "LEFT" if left is not None else                          "RIGHT" if right is not None else "NONE"
            cv2.putText(processed_frame, f"Lanes: {lane_status}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            cv2.putText(processed_frame, "SkyJames AI", (10, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
            if not self.frame_queue.full():
                self.frame_queue.put(processed_frame)
    
    def get_frame(self):
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return self.last_frame
    
    def get_frame_base64(self):
        frame = self.get_frame()
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            return base64.b64encode(buffer).decode('utf-8')
        return None
    
    def get_status(self):
        return {
            'is_capturing': self.is_capturing,
            'fps': self.fps,
            'frame_count': self.frame_count,
            'has_frame': self.last_frame is not None
        }
    
    def stop_camera(self):
        self.is_capturing = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.camera:
            self.camera.release()
            self.camera = None
        return {'status': 'success', 'message': 'Camera stopped'}
    
    def save_video(self, duration=10, output_path=None):
        if not self.is_capturing:
            return {'error': 'Camera not running'}
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"data/input/webcam_capture_{timestamp}.avi"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cap = cv2.VideoCapture(0)
        fps = 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed, left, right = self.detector.process_frame(frame)
            out.write(processed)
            frame_count += 1
        
        cap.release()
        out.release()
        
        return {
            'status': 'success',
            'path': output_path,
            'frames': frame_count,
            'duration': duration
        }

webcam = WebcamCapture()
