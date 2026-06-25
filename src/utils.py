"""
Utility functions for lane detection
"""

import cv2
import numpy as np
import os
from datetime import datetime

def ensure_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def get_timestamp():
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def resize_image(image, max_width=1280, max_height=720):
    """Resize image while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    if width > max_width or height > max_height:
        ratio = min(max_width/width, max_height/height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return cv2.resize(image, (new_width, new_height))
    return image

def overlay_text(image, text, position=(10, 30), 
                font_scale=0.7, color=(0, 255, 0), thickness=2):
    """Add text overlay to image"""
    cv2.putText(image, text, position, 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    return image

def calculate_slope(x1, y1, x2, y2):
    """Calculate slope between two points"""
    if x2 - x1 == 0:
        return None
    return (y2 - y1) / (x2 - x1)

def get_video_properties(video_path):
    """Get video properties"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    props = {
        'fps': int(cap.get(cv2.CAP_PROP_FPS)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    }
    cap.release()
    return props

def create_frame_grid(frames, titles=None, cols=2):
    """Create a grid of frames for visualization"""
    num_frames = len(frames)
    rows = (num_frames + cols - 1) // cols
    
    # Get max dimensions
    max_height = max(f.shape[0] for f in frames)
    max_width = max(f.shape[1] for f in frames)
    
    # Create grid
    grid = np.zeros((max_height * rows, max_width * cols, 3), dtype=np.uint8)
    
    for i, frame in enumerate(frames):
        row = i // cols
        col = i % cols
        h, w = frame.shape[:2]
        grid[row*max_height:row*max_height+h, 
             col*max_width:col*max_width+w] = frame
        
        if titles and i < len(titles):
            cv2.putText(grid, titles[i], 
                       (col*max_width + 10, row*max_height + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return grid
