"""
Safety Monitoring Layer
"""

import numpy as np
import cv2
from collections import deque

class SafetyMonitor:
    def __init__(self, config=None):
        self.config = config or Config()
        self.safety_violations = []
        self.violation_history = deque(maxlen=100)
        
        # Safety thresholds
        self.min_distance = 3.0
        self.max_steering_rate = 0.5
        self.min_lane_width = 2.5
        self.max_speed = 15.0
        
        self.prev_steering = 0.0
    
    def evaluate_safety(self, perception_result, prediction_result, planning_result, current_state):
        """Evaluate all safety checks"""
        violations = []
        
        # Check perception
        detections = perception_result.get('detections', [])
        lane_lines = perception_result.get('lane_lines', (None, None))
        
        for det in detections:
            if det['class_name'] in ['car', 'truck', 'pedestrian', 'bicycle']:
                bbox = det['bbox']
                height = bbox[3] - bbox[1]
                if height > 100:
                    violations.append(f"Obstacle detected: {det['class_name']}")
        
        # Check lane detection
        left_line, right_line = lane_lines
        if left_line is None or right_line is None:
            violations.append("Lane detection failed")
        
        is_safe = len(violations) == 0
        
        for violation in violations:
            self.safety_violations.append(violation)
            self.violation_history.append(violation)
        
        return is_safe, violations
    
    def get_safety_report(self):
        """Generate safety report"""
        return {
            'total_violations': len(self.safety_violations),
            'recent_violations': list(self.violation_history),
            'status': 'SAFE' if len(self.violation_history) == 0 else 'UNSAFE'
        }
    
    def visualize_safety(self, frame, is_safe, violations):
        """Visualize safety status on frame"""
        result = np.copy(frame)
        
        status_color = (0, 255, 0) if is_safe else (0, 0, 255)
        status_text = "SAFE" if is_safe else "UNSAFE"
        cv2.putText(result, f"SAFETY: {status_text}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        
        if violations:
            for i, violation in enumerate(violations[:3]):
                cv2.putText(result, violation, 
                           (10, 70 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 0, 255), 2)
        
        return result
