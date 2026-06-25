"""
SkyJames - Anomaly Detection
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from collections import deque
import json

class AnomalyDetector:
    def __init__(self, window_size=100, contamination=0.1):
        self.window_size = window_size
        self.contamination = contamination
        self.features = deque(maxlen=window_size)
        self.model = None
        self.anomalies = []
    
    def add_data(self, features):
        """Add new data point for anomaly detection"""
        self.features.append(features)
        
        if len(self.features) >= 100:
            self._train_model()
            return self._check_anomaly(features)
        return False
    
    def _train_model(self):
        """Train isolation forest on collected data"""
        data = np.array(self.features)
        if len(data) >= 100:
            self.model = IsolationForest(contamination=self.contamination, random_state=42)
            self.model.fit(data)
    
    def _check_anomaly(self, features):
        """Check if current features are anomalous"""
        if self.model is None:
            return False
        
        features = np.array(features).reshape(1, -1)
        prediction = self.model.predict(features)
        
        if prediction[0] == -1:
            self.anomalies.append({
                'features': features.tolist(),
                'timestamp': datetime.now().isoformat()
            })
            return True
        return False
    
    def get_anomalies(self, limit=10):
        return self.anomalies[-limit:]

# Example: Detect anomalies in FPS and detection counts
class SystemAnomalyDetector:
    def __init__(self):
        self.fps_detector = AnomalyDetector(contamination=0.05)
        self.detection_detector = AnomalyDetector(contamination=0.05)
    
    def check_system(self, fps, detections, processing_time):
        anomalies = []
        
        # Check FPS
        if self.fps_detector.add_data([fps]):
            anomalies.append(f"⚠️ Anomalous FPS: {fps:.1f}")
        
        # Check detections
        if self.detection_detector.add_data([detections]):
            anomalies.append(f"⚠️ Anomalous detections: {detections}")
        
        return anomalies
