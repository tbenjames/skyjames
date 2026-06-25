"""
SkyJames - Scene Detection
"""

import cv2
import numpy as np

class SceneDetector:
    def __init__(self):
        self.scenes = []
    
    def detect_scenes(self, video_path, threshold=30):
        """Detect scene changes using histogram differences"""
        cap = cv2.VideoCapture(video_path)
        prev_frame = None
        scene_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if prev_frame is not None:
                # Convert to grayscale and compare histograms
                gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                hist1 = cv2.calcHist([gray1], [0], None, [64], [0, 256])
                hist2 = cv2.calcHist([gray2], [0], None, [64], [0, 256])
                
                diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
                
                if diff > threshold:
                    scene_count += 1
                    self.scenes.append({
                        'scene_id': scene_count,
                        'frame': frame,
                        'timestamp': cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                    })
            
            prev_frame = frame
        
        cap.release()
        return self.scenes
