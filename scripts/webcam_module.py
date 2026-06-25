"""
SkyJames - Webcam Module
Handles webcam capture and processing
"""

import cv2
import numpy as np
import threading
import queue
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class WebcamManager:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.thread = None
        self.last_frame = None
        self.fps = 0
    
    def start(self, camera_id=0):
        """Start webcam capture"""
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
            
            self.is_running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            return {'status': 'success', 'message': 'Camera started'}
        except Exception as e:
            return {'error': str(e)}
    
    def _capture_loop(self):
        """Main capture loop"""
        frame_count = 0
        start_time = time.time()
        
        while self.is_running:
            if self.camera is None or not self.camera.isOpened():
                break
            
            ret, frame = self.camera.read()
            if not ret:
                break
            
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed > 0:
                self.fps = frame_count / elapsed
            
            # Add overlay
            cv2.putText(frame, f"SkyJames Webcam - FPS: {self.fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frames: {frame_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
            self.last_frame = frame
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
    
    def get_frame(self):
        """Get latest frame"""
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return self.last_frame
    
    def stop(self):
        """Stop webcam capture"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.camera:
            self.camera.release()
            self.camera = None
        return {'status': 'success', 'message': 'Camera stopped'}

# Global instance
webcam_manager = WebcamManager()
