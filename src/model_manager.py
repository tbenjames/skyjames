"""
SkyJames - Advanced Model Manager
Supports: YOLO11, ByteTrack, TwinLiteNet+, Pose Estimation, and more
"""

import cv2
import numpy as np
import torch
import time
from typing import Dict, List, Tuple, Optional
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config

class ModelManager:
    """Unified interface for all SkyJames models"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.models = {}
        self.active_models = []
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🚀 Model Manager initialized on {self.device}")
    
    def load_yolo11(self, model_name='yolo11n.pt'):
        """Load YOLO11 model"""
        try:
            from ultralytics import YOLO
            print(f"📦 Loading YOLO11: {model_name}")
            self.models['yolo'] = {
                'model': YOLO(model_name),
                'type': 'detection',
                'name': model_name
            }
            self.active_models.append('yolo')
            print(f"✅ YOLO11 loaded successfully")
            return self.models['yolo']
        except Exception as e:
            print(f"❌ Failed to load YOLO11: {e}")
            return None
    
    def load_yolo_seg(self, model_name='yolo11n-seg.pt'):
        """Load YOLO11 segmentation model"""
        try:
            from ultralytics import YOLO
            print(f"📦 Loading YOLO11 Segmentation: {model_name}")
            self.models['yolo_seg'] = {
                'model': YOLO(model_name),
                'type': 'segmentation',
                'name': model_name
            }
            self.active_models.append('yolo_seg')
            print(f"✅ YOLO11 Segmentation loaded")
            return self.models['yolo_seg']
        except Exception as e:
            print(f"❌ Failed to load YOLO11 Segmentation: {e}")
            return None
    
    def load_yolo_pose(self, model_name='yolo11n-pose.pt'):
        """Load YOLO11 pose estimation model"""
        try:
            from ultralytics import YOLO
            print(f"📦 Loading YOLO11 Pose: {model_name}")
            self.models['yolo_pose'] = {
                'model': YOLO(model_name),
                'type': 'pose',
                'name': model_name
            }
            self.active_models.append('yolo_pose')
            print(f"✅ YOLO11 Pose loaded")
            return self.models['yolo_pose']
        except Exception as e:
            print(f"❌ Failed to load YOLO11 Pose: {e}")
            return None
    
    def load_yolo_obb(self, model_name='yolo11n-obb.pt'):
        """Load YOLO11 oriented bounding box model"""
        try:
            from ultralytics import YOLO
            print(f"📦 Loading YOLO11 OBB: {model_name}")
            self.models['yolo_obb'] = {
                'model': YOLO(model_name),
                'type': 'obb',
                'name': model_name
            }
            self.active_models.append('yolo_obb')
            print(f"✅ YOLO11 OBB loaded")
            return self.models['yolo_obb']
        except Exception as e:
            print(f"❌ Failed to load YOLO11 OBB: {e}")
            return None
    
    def load_bytetrack(self):
        """Load ByteTrack for object tracking"""
        try:
            from boxmot import ByteTrack
            print("📦 Loading ByteTrack...")
            self.models['bytetrack'] = {
                'model': ByteTrack(),
                'type': 'tracking',
                'name': 'bytetrack'
            }
            self.active_models.append('bytetrack')
            print(f"✅ ByteTrack loaded")
            return self.models['bytetrack']
        except Exception as e:
            print(f"❌ Failed to load ByteTrack: {e}")
            return None
    
    def load_twinlitenet(self, model_path='models/twinlitenet_plus.pth'):
        """Load TwinLiteNet+ for lane segmentation"""
        try:
            # Import TwinLiteNet+ (requires git clone)
            sys.path.append('TwinLiteNetPlus')
            from models.model import TwinLiteNetPlus
            
            print(f"📦 Loading TwinLiteNet+ from {model_path}")
            model = TwinLiteNetPlus()
            
            if os.path.exists(model_path):
                model.load_state_dict(torch.load(model_path, map_location=self.device))
                model.to(self.device)
                model.eval()
            
            self.models['twinlitenet'] = {
                'model': model,
                'type': 'lane_segmentation',
                'name': 'twinlitenet_plus'
            }
            self.active_models.append('twinlitenet')
            print(f"✅ TwinLiteNet+ loaded")
            return self.models['twinlitenet']
        except Exception as e:
            print(f"❌ Failed to load TwinLiteNet+: {e}")
            return None
    
    def load_suscnnet(self, model_path='models/suscnnet.pth'):
        """Load SUSC-SNet for semantic segmentation"""
        try:
            print(f"📦 Loading SUSC-SNet from {model_path}")
            # Placeholder for SUSC-SNet
            self.models['suscnnet'] = {
                'model': None,
                'type': 'semantic_segmentation',
                'name': 'suscnnet',
                'path': model_path
            }
            self.active_models.append('suscnnet')
            print(f"✅ SUSC-SNet loaded (placeholder)")
            return self.models['suscnnet']
        except Exception as e:
            print(f"❌ Failed to load SUSC-SNet: {e}")
            return None
    
    def detect(self, frame, model_name='yolo'):
        """Run detection on a frame"""
        if model_name not in self.models:
            print(f"❌ Model {model_name} not loaded")
            return None
        
        model_data = self.models[model_name]
        model = model_data['model']
        model_type = model_data['type']
        
        if model_type == 'detection':
            return self._run_yolo_detection(frame, model)
        elif model_type == 'segmentation':
            return self._run_yolo_segmentation(frame, model)
        elif model_type == 'pose':
            return self._run_yolo_pose(frame, model)
        elif model_type == 'obb':
            return self._run_yolo_obb(frame, model)
        elif model_type == 'tracking':
            return self._run_tracking(frame, model)
        elif model_type == 'lane_segmentation':
            return self._run_lane_segmentation(frame, model)
        else:
            return None
    
    def _run_yolo_detection(self, frame, model):
        """Run YOLO detection"""
        results = model(frame)
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    'bbox': box.xyxy[0].tolist(),
                    'confidence': float(box.conf[0]),
                    'class_id': int(box.cls[0]),
                    'class_name': r.names[int(box.cls[0])]
                })
        return detections
    
    def _run_yolo_segmentation(self, frame, model):
        """Run YOLO segmentation"""
        results = model(frame)
        masks = []
        for r in results:
            if r.masks is not None:
                for mask, box in zip(r.masks.data, r.boxes):
                    masks.append({
                        'mask': mask.cpu().numpy(),
                        'bbox': box.xyxy[0].tolist(),
                        'class_name': r.names[int(box.cls[0])]
                    })
        return masks
    
    def _run_yolo_pose(self, frame, model):
        """Run YOLO pose estimation"""
        results = model(frame)
        poses = []
        for r in results:
            if r.keypoints is not None:
                for keypoints in r.keypoints.data:
                    poses.append({
                        'keypoints': keypoints.cpu().numpy(),
                        'bbox': r.boxes.xyxy[0].tolist() if r.boxes is not None else None
                    })
        return poses
    
    def _run_yolo_obb(self, frame, model):
        """Run YOLO oriented bounding box"""
        results = model(frame)
        obbs = []
        for r in results:
            if r.obb is not None:
                for obb in r.obb:
                    obbs.append({
                        'xyxyxyxy': obb.xyxyxyxy[0].tolist(),
                        'confidence': float(obb.conf[0]),
                        'class_name': r.names[int(obb.cls[0])]
                    })
        return obbs
    
    def _run_tracking(self, frame, model):
        """Run ByteTrack tracking"""
        # ByteTrack integration placeholder
        return {'tracked': True, 'count': 0}
    
    def _run_lane_segmentation(self, frame, model):
        """Run TwinLiteNet+ lane segmentation"""
        # Preprocess for TwinLiteNet+
        return {'lanes': None, 'drivable_area': None}
    
    def draw_detections(self, frame, detections, model_type='detection'):
        """Draw detections on frame"""
        result = frame.copy()
        
        if model_type == 'detection':
            for det in detections:
                x1, y1, x2, y2 = map(int, det['bbox'])
                label = f"{det['class_name']} {det['confidence']:.2f}"
                cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(result, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        elif model_type == 'segmentation' and detections:
            for det in detections:
                mask = det.get('mask')
                if mask is not None:
                    # Draw mask overlay
                    mask = mask.astype(np.uint8)
                    mask = cv2.resize(mask, (result.shape[1], result.shape[0]))
                    result[mask == 1] = result[mask == 1] * 0.5 + np.array([0, 255, 0]) * 0.5
        
        elif model_type == 'pose' and detections:
            for pose in detections:
                keypoints = pose.get('keypoints')
                if keypoints is not None:
                    # Draw skeleton
                    for kp in keypoints:
                        x, y, conf = kp
                        if conf > 0.5:
                            cv2.circle(result, (int(x), int(y)), 5, (0, 0, 255), -1)
        
        return result

# Global instance
model_manager = ModelManager()

def load_all_models():
    """Load all available models"""
    print("\n📦 Loading all SkyJames models...")
    print("=" * 50)
    
    # Load YOLO variants
    model_manager.load_yolo11()
    model_manager.load_yolo_seg()
    model_manager.load_yolo_pose()
    model_manager.load_yolo_obb()
    
    # Load tracking
    try:
        model_manager.load_bytetrack()
    except:
        print("⚠️ ByteTrack not available")
    
    print("\n✅ All models loaded!")
    print(f"Active models: {model_manager.active_models}")
    print("=" * 50)
    return model_manager
