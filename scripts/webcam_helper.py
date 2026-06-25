"""
SkyJames - Webcam Helper
Handles webcam operations across different platforms
"""

import cv2
import numpy as np
import os
import sys
import platform

def get_available_cameras():
    """Detect available cameras"""
    cameras = []
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                cap.release()
        except:
            pass
    return cameras

def get_camera_info(camera_id=0):
    """Get camera information"""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        return None
    
    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': int(cap.get(cv2.CAP_PROP_FPS)),
        'backend': cap.get(cv2.CAP_PROP_BACKEND)
    }
    cap.release()
    return info

def is_webcam_available():
    """Check if any webcam is available"""
    cameras = get_available_cameras()
    return len(cameras) > 0

def get_system_info():
    """Get system information for webcam compatibility"""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }
