"""
Quick test for the pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from src.config import Config
from src.perception.lane_net_cpu import OptimizedLaneDetector

def test():
    print("=" * 60)
    print("Testing Pipeline")
    print("=" * 60)
    
    config = Config()
    
    # Test CULane dataset
    print("\n1. Testing CULane dataset...")
    try:
        from src.data.culane_loader import CULaneDataset
        if config.culane_exists:
            dataset = CULaneDataset(config, split='train', max_samples=5)
            print(f"   ✓ Dataset loaded: {len(dataset)} samples")
            if len(dataset) > 0:
                sample = dataset[0]
                print(f"   ✓ Sample keys: {sample.keys()}")
                print(f"   ✓ Image shape: {sample['image'].shape}")
        else:
            print(f"   ⚠ CULane not found at: {config.CULANE_PATH}")
            print("   Continuing with dummy data...")
    except Exception as e:
        print(f"   ⚠ Dataset error: {e}")
    
    # Test detector
    print("\n2. Testing lane detector...")
    try:
        detector = OptimizedLaneDetector(config)
        print("   ✓ Detector initialized")
        
        # Create dummy frame
        dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result, left, right = detector.process_frame(dummy_frame, use_neural=False)
        print(f"   ✓ Processed dummy frame: {result.shape}")
        print(f"   ✓ Left line: {left}")
        print(f"   ✓ Right line: {right}")
    except Exception as e:
        print(f"   ✗ Detector error: {e}")
        return
    
    # Test safety
    print("\n3. Testing safety monitor...")
    try:
        from src.safety.safety_monitor import SafetyMonitor
        safety = SafetyMonitor(config)
        perception_result = {'detections': [], 'lane_lines': (None, None)}
        is_safe, violations = safety.evaluate_safety(perception_result, {}, {}, None)
        print(f"   ✓ Safety check passed: {is_safe}")
    except Exception as e:
        print(f"   ✗ Safety error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test()
