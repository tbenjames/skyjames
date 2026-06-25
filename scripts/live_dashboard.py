"""
Live statistics dashboard for World Cup analysis
"""

import json
import os
import time
import glob

def show_dashboard():
    """Display live dashboard"""
    
    print("\n" + "=" * 60)
    print("🏆 WORLD CUP 2026 - LIVE DASHBOARD")
    print("=" * 60)
    
    # Find latest stats
    stats_files = glob.glob("data/output/worldcup_analysis_*_stats.json")
    if stats_files:
        latest = max(stats_files, key=os.path.getctime)
        with open(latest, 'r') as f:
            stats = json.load(f)
        
        print(f"\n📊 Match: Portugal vs Uzbekistan")
        print(f"⚽ Final Score: Portugal {stats.get('goals', {}).get('Portugal', 0)} - {stats.get('goals', {}).get('Uzbekistan', 0)} Uzbekistan")
        print(f"📹 Frames Processed: {stats.get('total_frames', 0)}")
        
        possession = stats.get('possession', {})
        if possession:
            total = possession.get('Portugal', 0) + possession.get('Uzbekistan', 0)
            if total > 0:
                print(f"⏱️ Possession: Portugal {possession.get('Portugal', 0)/total*100:.1f}% - Uzbekistan {possession.get('Uzbekistan', 0)/total*100:.1f}%")
    
    print("\n📁 Latest Outputs:")
    videos = glob.glob("data/output/worldcup_*.mp4")
    if videos:
        latest_video = max(videos, key=os.path.getctime)
        print(f"  🎥 {os.path.basename(latest_video)}")
    
    print("=" * 60)

if __name__ == "__main__":
    show_dashboard()
