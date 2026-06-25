"""
Performance testing for SkyJames
"""

import time
import statistics
import cv2
import numpy as np
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

def test_processing_speed():
    """Test processing speed"""
    detector = OptimizedLaneDetector(Config())
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    times = []
    for _ in range(50):
        start = time.time()
        detector.process_frame(frame, use_neural=False)
        times.append(time.time() - start)
    
    avg = statistics.mean(times)
    fps = 1.0 / avg
    
    print(f"📊 Processing Speed:")
    print(f"  Avg time: {avg*1000:.2f}ms")
    print(f"  FPS: {fps:.2f}")
    print(f"  Min: {min(times)*1000:.2f}ms")
    print(f"  Max: {max(times)*1000:.2f}ms")
    
    return fps > 15  # Should be at least 15 FPS

if __name__ == "__main__":
    test_processing_speed()
