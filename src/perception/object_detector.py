"""
Object Detection using YOLO
"""

import cv2
import numpy as np
from src.config import Config

class ObjectDetector:
    def __init__(self, config=None):
        self.config = config or Config()
        self.model = None
        self.use_yolo = False
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.config.YOLO_MODEL)
            if hasattr(self.model, 'to'):
                self.model.to('cpu')
            self.use_yolo = True
            print(f"YOLO loaded: {self.config.YOLO_MODEL}")
        except ImportError:
            print("YOLO not available - using dummy detector")
        except Exception as e:
            print(f"Error loading YOLO: {e}")
    
    def detect_objects(self, frame):
        """Detect objects and return bounding boxes"""
        if not self.use_yolo or self.model is None:
            return []
        
        try:
            results = self.model(frame, conf=self.config.OBJECT_CONFIDENCE, device='cpu')[0]
            detections = []
            
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = results.names[class_id]
                
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': confidence,
                    'class_name': class_name,
                    'class_id': class_id
                })
            
            return detections
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes on frame"""
        result = np.copy(frame)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class_name']} {det['confidence']:.2f}"
            
            cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(result, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return result
