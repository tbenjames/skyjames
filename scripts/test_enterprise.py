"""
Test SkyJames Enterprise Features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_all():
    print("🚀 Testing SkyJames Enterprise Features")
    print("=" * 60)
    
    # 1. Test MLflow
    print("\n1️⃣ Testing MLflow...")
    try:
        from src.enterprise import SkyJamesMLflow
        tracker = SkyJamesMLflow()
        print("   ✅ MLflow initialized")
    except Exception as e:
        print(f"   ❌ MLflow error: {e}")
    
    # 2. Test Metrics
    print("\n2️⃣ Testing Metrics...")
    try:
        from src.enterprise import metrics
        metrics.record_frame(30, 5, 0.05)
        print("   ✅ Metrics recorded")
    except Exception as e:
        print(f"   ❌ Metrics error: {e}")
    
    # 3. Test A/B Testing
    print("\n3️⃣ Testing A/B Testing...")
    try:
        from src.enterprise import ABTesting
        ab = ABTesting()
        exp = ab.start_experiment('test', ['v1', 'v2'])
        print(f"   ✅ A/B test started: {exp['name']}")
    except Exception as e:
        print(f"   ❌ A/B error: {e}")
    
    # 4. Test BI Export
    print("\n4️⃣ Testing BI Export...")
    try:
        from src.enterprise import BIExporter
        exporter = BIExporter()
        data = [{'test': 1, 'value': 100}]
        path = exporter.export_video_analytics(data, 'json')
        print(f"   ✅ BI export created: {path}")
    except Exception as e:
        print(f"   ❌ BI error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Enterprise test complete!")

if __name__ == "__main__":
    test_all()
