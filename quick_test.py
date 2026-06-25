"""
Quick test for SkyJames models
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Testing SkyJames Models")
print("=" * 40)

# Test imports
try:
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
except Exception as e:
    print(f"❌ NumPy: {e}")

try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except Exception as e:
    print(f"❌ OpenCV: {e}")

try:
    from ultralytics import YOLO
    print("✅ Ultralytics imported")
except Exception as e:
    print(f"❌ Ultralytics: {e}")

try:
    from src.model_manager_no_track import load_all_models
    model_manager = load_all_models()
    print(f"✅ Models loaded: {model_manager.active_models}")
except Exception as e:
    print(f"❌ Model Manager: {e}")

print("=" * 40)
