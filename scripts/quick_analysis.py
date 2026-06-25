"""
Quick analysis of comparison results
"""

import os
import glob
import json
from datetime import datetime

def analyze_results():
    """Analyze test results"""
    
    print("=" * 60)
    print("ANALYZING TEST RESULTS")
    print("=" * 60)
    
    # Check for output files
    output_dir = "data/output"
    files = {
        'comparison_videos': glob.glob(f"{output_dir}/comparison_video_*.mp4"),
        'comparison_plots': glob.glob(f"{output_dir}/comparison_*.png"),
        'reports': glob.glob(f"{output_dir}/report_*.json"),
        'frames': glob.glob(f"{output_dir}/comparison_frames/*.jpg")
    }
    
    print(f"\nFound:")
    for key, items in files.items():
        print(f"  {key}: {len(items)}")
    
    if files['comparison_videos']:
        latest = max(files['comparison_videos'], key=os.path.getctime)
        size = os.path.getsize(latest) / (1024 * 1024)
        print(f"\nLatest comparison video: {os.path.basename(latest)} ({size:.2f} MB)")
        print(f"  Play with: python scripts/play_video.py {latest}")
    
    if files['comparison_plots']:
        latest = max(files['comparison_plots'], key=os.path.getctime)
        print(f"\nLatest comparison plot: {os.path.basename(latest)}")
        print(f"  View with: open {latest}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_results()
