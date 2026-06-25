"""
Simple dashboard showing pipeline status
"""

import os
import glob
import time
from datetime import datetime

def show_dashboard():
    """Display pipeline status dashboard"""
    
    print("\n" + "=" * 60)
    print("LANE DETECTION PIPELINE - DASHBOARD")
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Model status
    model_path = "models/lane_net_optimized.pth"
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✓ Model: {model_path} ({size:.2f} MB)")
    else:
        print("✗ Model: Not found")
    
    # Check checkpoints
    checkpoints = glob.glob("models/checkpoint_epoch_*.pth")
    if checkpoints:
        latest = max(checkpoints, key=os.path.getctime)
        print(f"✓ Latest checkpoint: {os.path.basename(latest)}")
        print(f"  Total checkpoints: {len(checkpoints)}")
    
    # Output videos
    outputs = glob.glob("data/output/*.mp4")
    if outputs:
        latest = max(outputs, key=os.path.getctime)
        size = os.path.getsize(latest) / (1024 * 1024)
        print(f"✓ Latest output: {os.path.basename(latest)} ({size:.2f} MB)")
        print(f"  Total outputs: {len(outputs)}")
    
    # Input videos
    inputs = glob.glob("data/input/*.mp4") + glob.glob("data/input/*.avi")
    if inputs:
        print(f"✓ Input videos: {len(inputs)}")
    
    # Disk usage
    import shutil
    total, used, free = shutil.disk_usage("/Users/apple/lane-detection")
    print(f"✓ Disk space: {free / (1024**3):.1f} GB free")
    
    print("=" * 60)
    print("\nQuick Commands:")
    print("  python scripts/run_pipeline_with_model.py  - Process video with NN")
    print("  python scripts/webcam_pipeline.py          - Real-time webcam")
    print("  python scripts/production_pipeline_complete.py - Full pipeline")
    print("=" * 60)

if __name__ == "__main__":
    show_dashboard()
