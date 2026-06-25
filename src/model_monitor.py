"""
SkyJames - Model Performance Monitoring
"""

import numpy as np
from collections import deque
from datetime import datetime

class ModelMonitor:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.metrics = {
            'accuracy': deque(maxlen=window_size),
            'fps': deque(maxlen=window_size),
            'detection_time': deque(maxlen=window_size)
        }
        self.alerts = []
    
    def record_prediction(self, accuracy, fps, time_ms):
        self.metrics['accuracy'].append(accuracy)
        self.metrics['fps'].append(fps)
        self.metrics['detection_time'].append(time_ms)
        self._check_alerts()
    
    def _check_alerts(self):
        if len(self.metrics['accuracy']) >= 10:
            avg_acc = np.mean(self.metrics['accuracy'])
            if avg_acc < 0.7:
                self.alerts.append({
                    'type': 'accuracy_drop',
                    'message': f'Low accuracy detected: {avg_acc:.2%}',
                    'timestamp': datetime.now().isoformat()
                })
        
        if len(self.metrics['fps']) >= 10:
            avg_fps = np.mean(self.metrics['fps'])
            if avg_fps < 15:
                self.alerts.append({
                    'type': 'performance_drop',
                    'message': f'Low FPS detected: {avg_fps:.1f}',
                    'timestamp': datetime.now().isoformat()
                })
    
    def get_stats(self):
        return {
            'avg_accuracy': np.mean(self.metrics['accuracy']) if self.metrics['accuracy'] else 0,
            'avg_fps': np.mean(self.metrics['fps']) if self.metrics['fps'] else 0,
            'avg_time': np.mean(self.metrics['detection_time']) if self.metrics['detection_time'] else 0,
            'total_predictions': len(self.metrics['accuracy']),
            'alerts': len(self.alerts)
        }
