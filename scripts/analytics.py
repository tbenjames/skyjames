"""
Real-time analytics for lane detection
"""

import json
import time
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class AnalyticsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = time.time()
    
    def record_frame(self, fps, detection_count, safety_status):
        """Record metrics for a frame"""
        timestamp = time.time() - self.start_time
        self.metrics['timestamp'].append(timestamp)
        self.metrics['fps'].append(fps)
        self.metrics['detections'].append(detection_count)
        self.metrics['safety'].append(1 if safety_status else 0)
        self.metrics['time'].append(timestamp)
    
    def get_stats(self):
        """Get current statistics"""
        if not self.metrics['fps']:
            return {}
        
        return {
            'avg_fps': sum(self.metrics['fps'][-30:]) / min(30, len(self.metrics['fps'])),
            'total_frames': len(self.metrics['fps']),
            'avg_detections': sum(self.metrics['detections'][-30:]) / min(30, len(self.metrics['detections'])),
            'safety_rate': sum(self.metrics['safety']) / len(self.metrics['safety']) * 100,
            'runtime': time.time() - self.start_time
        }
    
    def plot_metrics(self, save_path=None):
        """Plot metrics visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # FPS over time
        axes[0, 0].plot(self.metrics['timestamp'], self.metrics['fps'])
        axes[0, 0].set_title('FPS Over Time')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('FPS')
        axes[0, 0].grid(True)
        
        # Detections over time
        axes[0, 1].plot(self.metrics['timestamp'], self.metrics['detections'])
        axes[0, 1].set_title('Detections Over Time')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Detection Count')
        axes[0, 1].grid(True)
        
        # Safety histogram
        axes[1, 0].hist(self.metrics['safety'], bins=[-0.5, 0.5, 1.5], 
                       labels=['Unsafe', 'Safe'], rwidth=0.8)
        axes[1, 0].set_title('Safety Distribution')
        axes[1, 0].set_xlabel('Safety Status')
        axes[1, 0].set_ylabel('Count')
        
        # Runtime
        axes[1, 1].text(0.5, 0.5, f"Total Runtime: {self.get_stats().get('runtime', 0):.1f}s\n"
                        f"Total Frames: {self.get_stats().get('total_frames', 0)}\n"
                        f"Avg FPS: {self.get_stats().get('avg_fps', 0):.1f}\n"
                        f"Safety Rate: {self.get_stats().get('safety_rate', 0):.1f}%",
                        ha='center', va='center', fontsize=12)
        axes[1, 1].set_title('Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
        
        plt.show()
    
    def save_to_json(self, path="data/output/analytics.json"):
        """Save metrics to JSON"""
        with open(path, 'w') as f:
            json.dump(dict(self.metrics), f, indent=2)
        print(f"✅ Analytics saved: {path}")

if __name__ == "__main__":
    # Demo usage
    collector = AnalyticsCollector()
    
    # Simulate data
    for i in range(100):
        collector.record_frame(
            fps=np.random.uniform(20, 35),
            detection_count=np.random.randint(0, 5),
            safety_status=np.random.choice([True, False], p=[0.8, 0.2])
        )
        time.sleep(0.05)
    
    # Show results
    print("Statistics:", collector.get_stats())
    collector.plot_metrics("data/output/analytics_plot.png")
