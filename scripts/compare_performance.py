"""
Compare performance of traditional vs neural network
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import time
import numpy as np
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

def compare():
    config = Config()
    
    print("=" * 60)
    print("Performance Comparison")
    print("=" * 60)
    
    # Load model
    model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    detector = OptimizedLaneDetector(config, model_path=model_path if os.path.exists(model_path) else None)
    
    # Create test frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    print("\nTesting Traditional Method...")
    times_trad = []
    for i in range(20):
        start = time.time()
        _, left, right = detector.process_frame(frame, use_neural=False)
        elapsed = time.time() - start
        times_trad.append(elapsed)
    
    print("\nTesting Neural Network...")
    times_nn = []
    for i in range(20):
        start = time.time()
        _, left, right = detector.process_frame(frame, use_neural=True)
        elapsed = time.time() - start
        times_nn.append(elapsed)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Traditional Method:")
    print(f"  Avg: {np.mean(times_trad)*1000:.2f}ms")
    print(f"  FPS: {1.0/np.mean(times_trad):.2f}")
    print(f"  Min: {np.min(times_trad)*1000:.2f}ms")
    print(f"  Max: {np.max(times_trad)*1000:.2f}ms")
    print()
    print(f"Neural Network:")
    print(f"  Avg: {np.mean(times_nn)*1000:.2f}ms")
    print(f"  FPS: {1.0/np.mean(times_nn):.2f}")
    print(f"  Min: {np.min(times_nn)*1000:.2f}ms")
    print(f"  Max: {np.max(times_nn)*1000:.2f}ms")
    print()
    speedup = np.mean(times_trad) / np.mean(times_nn)
    print(f"Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    compare()
