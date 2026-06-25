
"""
SkyJames - Prometheus Metrics
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY

class SkyJamesMetrics:
    def __init__(self):
        self.frames_processed = Counter("skyjames_frames_processed", "Total frames processed")
        self.detections_count = Counter("skyjames_detections_count", "Total detections made")
        self.errors_count = Counter("skyjames_errors_count", "Total errors occurred")
        
        self.current_fps = Gauge("skyjames_current_fps", "Current FPS")
        self.processing_latency = Gauge("skyjames_processing_latency", "Processing latency in ms")
        self.active_connections = Gauge("skyjames_active_connections", "Active connections")
        self.memory_usage = Gauge("skyjames_memory_usage", "Memory usage in MB")
        
        self.detection_time = Histogram("skyjames_detection_time_seconds", "Detection time in seconds",
                                        buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0])
    
    def record_frame(self, fps, detection_count, processing_time):
        self.frames_processed.inc()
        self.detections_count.inc(detection_count)
        self.current_fps.set(fps)
        self.processing_latency.set(processing_time * 1000)
        self.detection_time.observe(processing_time)
    
    def record_error(self):
        self.errors_count.inc()
    
    def update_system_metrics(self, memory_mb, connections):
        self.memory_usage.set(memory_mb)
        self.active_connections.set(connections)
    
    def get_metrics(self):
        return generate_latest(REGISTRY)

metrics = SkyJamesMetrics()
print("✅ Metrics module initialized")
