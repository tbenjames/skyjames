"""
SkyJames - Prometheus Metrics Integration
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
import time

# Define metrics
class SkyJamesMetrics:
    def __init__(self):
        # Counters
        self.frames_processed = Counter('skyjames_frames_processed', 'Total frames processed')
        self.detections_count = Counter('skyjames_detections_count', 'Total detections made')
        self.errors_count = Counter('skyjames_errors_count', 'Total errors occurred')
        
        # Gauges
        self.current_fps = Gauge('skyjames_current_fps', 'Current FPS')
        self.processing_latency = Gauge('skyjames_processing_latency', 'Processing latency in ms')
        self.active_connections = Gauge('skyjames_active_connections', 'Active connections')
        self.memory_usage = Gauge('skyjames_memory_usage', 'Memory usage in MB')
        
        # Histograms
        self.detection_time = Histogram('skyjames_detection_time_seconds', 'Detection time in seconds',
                                        buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0])
        self.frame_size = Histogram('skyjames_frame_size_bytes', 'Frame size in bytes',
                                    buckets=[1024, 10240, 102400, 1048576, 10485760])
    
    def record_frame(self, fps, detection_count, processing_time):
        """Record frame metrics"""
        self.frames_processed.inc()
        self.detections_count.inc(detection_count)
        self.current_fps.set(fps)
        self.processing_latency.set(processing_time * 1000)  # Convert to ms
        self.detection_time.observe(processing_time)
    
    def record_error(self):
        """Record error"""
        self.errors_count.inc()
    
    def update_system_metrics(self, memory_mb, connections):
        """Update system metrics"""
        self.memory_usage.set(memory_mb)
        self.active_connections.set(connections)
    
    def get_metrics(self):
        """Get all metrics in Prometheus format"""
        return generate_latest(REGISTRY)

# Global metrics instance
metrics = SkyJamesMetrics()
