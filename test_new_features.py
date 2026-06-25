"""
Test all new SkyJames features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Testing SkyJames New Features")
print("=" * 50)

# Test 1: Video Analytics
try:
    from src.video_analytics_lstm import VideoAnalytics
    va = VideoAnalytics()
    print("✅ Video Analytics: OK")
except Exception as e:
    print(f"❌ Video Analytics: {e}")

# Test 2: AutoML
try:
    from src.automl import AutoMLPipeline
    aml = AutoMLPipeline([])
    print("✅ AutoML: OK")
except Exception as e:
    print(f"❌ AutoML: {e}")

# Test 3: Active Learning
try:
    from src.active_learning import ActiveLearner
    al = ActiveLearner()
    print("✅ Active Learning: OK")
except Exception as e:
    print(f"❌ Active Learning: {e}")

# Test 4: Notification System
try:
    from src.notification_system import NotificationSystem
    ns = NotificationSystem()
    print("✅ Notification System: OK")
except Exception as e:
    print(f"❌ Notification System: {e}")

# Test 5: Model Optimizer
try:
    from src.model_optimizer import ModelOptimizer
    mo = ModelOptimizer(None)
    print("✅ Model Optimizer: OK")
except Exception as e:
    print(f"❌ Model Optimizer: {e}")

print("=" * 50)
print("✅ Test complete!")
