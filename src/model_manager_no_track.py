"""
SkyJames - Model Manager (Clean Version)
Exactly 4 models: YOLO11, YOLO11-seg, YOLO11-pose, YOLO11-obb
No print statements, optimized for speed
"""

import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config

class ModelManager:
    def __init__(self, config=None):
        self.config = config or Config()
        self.models = {}
        self.active_models = []
        self.device = 'cpu'
        self._loaded = False
    
    def load_yolo11(self):
        """Load YOLO11 detection model"""
        try:
            from ultralytics import YOLO
            if 'yolo' not in self.models:
                self.models['yolo'] = {
                    'model': YOLO('yolo11n.pt'),
                    'type': 'detection',
                    'name': 'yolo11n.pt'
                }
                self.active_models.append('yolo')
        except:
            pass
    
    def load_yolo_seg(self):
        """Load YOLO11 segmentation model"""
        try:
            from ultralytics import YOLO
            if 'yolo_seg' not in self.models:
                self.models['yolo_seg'] = {
                    'model': YOLO('yolo11n-seg.pt'),
                    'type': 'segmentation',
                    'name': 'yolo11n-seg.pt'
                }
                self.active_models.append('yolo_seg')
        except:
            pass
    
    def load_yolo_pose(self):
        """Load YOLO11 pose estimation model"""
        try:
            from ultralytics import YOLO
            if 'yolo_pose' not in self.models:
                self.models['yolo_pose'] = {
                    'model': YOLO('yolo11n-pose.pt'),
                    'type': 'pose',
                    'name': 'yolo11n-pose.pt'
                }
                self.active_models.append('yolo_pose')
        except:
            pass
    
    def load_yolo_obb(self):
        """Load YOLO11 oriented bounding box model"""
        try:
            from ultralytics import YOLO
            if 'yolo_obb' not in self.models:
                self.models['yolo_obb'] = {
                    'model': YOLO('yolo11n-obb.pt'),
                    'type': 'obb',
                    'name': 'yolo11n-obb.pt'
                }
                self.active_models.append('yolo_obb')
        except:
            pass
    
    def detect(self, frame, model_name='yolo'):
        """Run detection with specified model"""
        if model_name not in self.models:
            return []
        
        model_data = self.models[model_name]
        model = model_data['model']
        model_type = model_data['type']
        
        try:
            results = model(frame)
            detections = []
            
            if model_type == 'detection':
                for r in results:
                    if r.boxes is not None:
                        for box in r.boxes:
                            detections.append({
                                'bbox': box.xyxy[0].tolist(),
                                'confidence': float(box.conf[0]),
                                'class_id': int(box.cls[0]),
                                'class_name': r.names[int(box.cls[0])]
                            })
            elif model_type == 'segmentation':
                for r in results:
                    if r.masks is not None and r.boxes is not None:
                        for mask, box in zip(r.masks.data, r.boxes):
                            detections.append({
                                'mask': mask.cpu().numpy(),
                                'bbox': box.xyxy[0].tolist(),
                                'class_name': r.names[int(box.cls[0])]
                            })
            elif model_type == 'pose':
                for r in results:
                    if r.keypoints is not None:
                        for keypoints in r.keypoints.data:
                            detections.append({
                                'keypoints': keypoints.cpu().numpy(),
                                'bbox': r.boxes.xyxy[0].tolist() if r.boxes is not None else None
                            })
            elif model_type == 'obb':
                for r in results:
                    if r.obb is not None:
                        for obb in r.obb:
                            detections.append({
                                'xyxyxyxy': obb.xyxyxyxy[0].tolist(),
                                'confidence': float(obb.conf[0]),
                                'class_name': r.names[int(obb.cls[0])]
                            })
            
            return detections
        except:
            return []
    
    def draw_detections(self, frame, detections, model_type='detection'):
        """Draw detections on frame"""
        result = frame.copy()
        if not detections:
            return result
        
        if model_type == 'detection':
            for det in detections:
                if 'bbox' in det:
                    x1, y1, x2, y2 = map(int, det['bbox'])
                    label = f"{det.get('class_name', 'object')} {det.get('confidence', 0):.2f}"
                    cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(result, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        elif model_type == 'segmentation':
            for det in detections:
                mask = det.get('mask')
                if mask is not None:
                    mask = mask.astype(np.uint8)
                    mask = cv2.resize(mask, (result.shape[1], result.shape[0]))
                    result[mask == 1] = result[mask == 1] * 0.5 + np.array([0, 255, 0]) * 0.5
        
        elif model_type == 'pose':
            for pose in detections:
                keypoints = pose.get('keypoints')
                if keypoints is not None:
                    for kp in keypoints:
                        if len(kp) >= 3 and kp[2] > 0.5:
                            cv2.circle(result, (int(kp[0]), int(kp[1])), 5, (0, 0, 255), -1)
        
        return result

# Global instance
model_manager = ModelManager()

def load_all_models():
    """Load exactly 4 models: YOLO11, YOLO11-seg, YOLO11-pose, YOLO11-obb"""
    if model_manager._loaded:
        return model_manager
    
    # Load exactly 4 models
    model_manager.load_yolo11()
    model_manager.load_yolo_seg()
    model_manager.load_yolo_pose()
    model_manager.load_yolo_obb()
    
    model_manager._loaded = True
    return model_manager
