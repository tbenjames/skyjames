"""
SkyJames - Universal Webcam Module
Works on: Desktop (Windows/Mac/Linux) and Mobile (iOS/Android)
"""

import cv2
import numpy as np
import streamlit as st
import time
import threading
import queue
import os
import sys
from PIL import Image
import io

class UniversalWebcam:
    """Universal webcam handler for all devices"""
    
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.thread = None
        self.last_frame = None
        self.fps = 0
        self.frame_count = 0
        self.start_time = None
        self.device_type = self._detect_device()
    
    def _detect_device(self):
        """Detect if running on mobile or desktop"""
        import platform
        system = platform.system().lower()
        if 'android' in system or 'ios' in system:
            return 'mobile'
        return 'desktop'
    
    def start(self, camera_id=0):
        """Start webcam capture"""
        try:
            # Try different backends for compatibility
            backends = [
                cv2.CAP_ANY,
                cv2.CAP_V4L2,  # Linux
                cv2.CAP_DSHOW,  # Windows DirectShow
                cv2.CAP_MSMF,   # Windows Media Foundation
                cv2.CAP_AVFOUNDATION  # Mac
            ]
            
            for backend in backends:
                try:
                    self.cap = cv2.VideoCapture(camera_id, backend)
                    if self.cap.isOpened():
                        break
                except:
                    continue
            
            # If still not opened, try default
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(camera_id)
            
            if not self.cap.isOpened():
                # Try alternative camera IDs for mobile
                for alt_id in [1, 2, -1, 'http://localhost:8080/video']:
                    try:
                        self.cap = cv2.VideoCapture(alt_id)
                        if self.cap.isOpened():
                            break
                    except:
                        continue
            
            if not self.cap.isOpened():
                return {'error': 'No camera detected'}
            
            # Set properties for compatibility
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_running = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            return {'status': 'success', 'message': 'Camera started', 'device': self.device_type}
        except Exception as e:
            return {'error': str(e)}
    
    def _capture_loop(self):
        """Main capture loop"""
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                break
            
            ret, frame = self.cap.read()
            if not ret:
                break
            
            self.frame_count += 1
            elapsed = time.time() - self.start_time if self.start_time else 0
            if elapsed > 0:
                self.fps = self.frame_count / elapsed
            
            # Add overlay
            cv2.putText(frame, f"SkyJames • {self.fps:.1f} FPS", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frames: {self.frame_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            self.last_frame = frame
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
    
    def get_frame(self):
        """Get latest frame"""
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return self.last_frame
    
    def get_frame_bytes(self):
        """Get frame as bytes for streaming"""
        frame = self.get_frame()
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        return None
    
    def stop(self):
        """Stop webcam capture"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
            self.cap = None
        return {'status': 'success', 'message': 'Camera stopped'}
    
    def get_status(self):
        """Get camera status"""
        return {
            'is_running': self.is_running,
            'fps': self.fps,
            'frame_count': self.frame_count,
            'device': self.device_type,
            'has_frame': self.last_frame is not None
        }

# Global instance
webcam = UniversalWebcam()
