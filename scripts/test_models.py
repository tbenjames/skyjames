"""
SkyJames - Comprehensive Model Test
Tests all models and saves results
"""

import cv2
import numpy as np
import os
import sys
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model_manager import load_all_models, model_manager

def test_performance():
    """Test model performance"""
    print("📊 Testing Model Performance")
    print("=" * 50)
    
    # Create test image
    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    results = []
    
    for model_name in model_manager.active_models:
        print(f"\n⏱️ Testing {model_name}...")
        
        # Warmup
        for _ in range(5):
            model_manager.detect(test_img, model_name)
        
        # Benchmark
        times = []
        for _ in range(20):
            start = time.time()
            model_manager.detect(test_img, model_name)
            times.append(time.time() - start)
        
        avg_time = np.mean(times)
        fps = 1.0 / avg_time
        
        results.append({
            'model': model_name,
            'avg_time_ms': avg_time * 1000,
            'fps': fps
        })
        
        print(f"   Avg: {avg_time*1000:.2f}ms, FPS: {fps:.1f}")
    
    print("\n" + "=" * 50)
    print("📊 Performance Summary:")
    for r in results:
        print(f"  {r['model']}: {r['fps']:.1f} FPS ({r['avg_time_ms']:.1f}ms)")
    
    return results

def test_on_samples():
    """Test models on sample images"""
    print("\n📸 Testing on sample images...")
    print("=" * 50)
    
    # Create sample images
    samples = [
        {'name': 'road', 'generate': lambda: cv2.imread('data/input/test_image.jpg')},
        {'name': 'sports', 'generate': lambda: np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)}
    ]
    
    for model_name in model_manager.active_models:
        print(f"\n📊 Testing {model_name} on samples...")
        for sample in samples:
            img = sample['generate']()
            if img is not None:
                detections = model_manager.detect(img, model_name)
                drawn = model_manager.draw_detections(img, detections,
                                                      model_manager.models[model_name]['type'])
                
                output_path = f"data/output/{model_name}_{sample['name']}.jpg"
                cv2.imwrite(output_path, drawn)
                print(f"   ✅ Saved: {output_path}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SkyJames Model Test Suite")
    print("=" * 60)
    
    # Load models
    load_all_models()
    
    # Run tests
    test_performance()
    test_on_samples()
    
    print("\n" + "=" * 60)
    print("✅ All tests complete!")
    print("📁 Results saved in data/output/")
    print("=" * 60)
