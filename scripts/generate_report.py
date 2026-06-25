"""
Generate comprehensive test report
"""

import os
import glob
import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def generate_report():
    """Generate a test report with all results"""
    
    print("=" * 60)
    print("GENERATING TEST REPORT")
    print("=" * 60)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'models': {},
        'videos': [],
        'comparisons': []
    }
    
    # Check model
    model_path = "models/lane_net_optimized.pth"
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / (1024 * 1024)
        report['models']['optimized'] = {
            'path': model_path,
            'size_mb': size
        }
        print(f"✓ Model: {size:.2f} MB")
    
    # Check checkpoints
    checkpoints = glob.glob("models/checkpoint_epoch_*.pth")
    if checkpoints:
        report['models']['checkpoints'] = len(checkpoints)
        print(f"✓ Checkpoints: {len(checkpoints)}")
    
    # Check outputs
    outputs = glob.glob("data/output/*.mp4")
    if outputs:
        latest = max(outputs, key=os.path.getctime)
        size = os.path.getsize(latest) / (1024 * 1024)
        report['videos'].append({
            'path': latest,
            'size_mb': size,
            'timestamp': datetime.fromtimestamp(os.path.getctime(latest)).isoformat()
        })
        print(f"✓ Latest output: {os.path.basename(latest)} ({size:.2f} MB)")
    
    # Check comparison frames
    comparison_frames = glob.glob("data/output/comparison_frames/*.jpg")
    if comparison_frames:
        print(f"✓ Comparison frames: {len(comparison_frames)}")
    
    # Check comparison plots
    plots = glob.glob("data/output/comparison_*.png")
    if plots:
        print(f"✓ Comparison plots: {len(plots)}")
    
    # Save report
    report_path = f"data/output/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("data/output", exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved: {report_path}")
    
    # Create summary text
    summary_path = report_path.replace('.json', '.txt')
    with open(summary_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("LANE DETECTION PIPELINE - TEST REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if 'optimized' in report['models']:
            f.write(f"Model: {report['models']['optimized']['size_mb']:.2f} MB\n")
        
        if 'checkpoints' in report['models']:
            f.write(f"Checkpoints: {report['models']['checkpoints']}\n")
        
        f.write(f"\nVideos processed: {len(report['videos'])}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 60 + "\n")
    
    print(f"✅ Summary report: {summary_path}")
    
    return report

if __name__ == "__main__":
    generate_report()
