"""
View World Cup analysis statistics
"""

import json
import os
import glob
from datetime import datetime

def view_stats():
    """View World Cup stats from analysis"""
    
    print("=" * 60)
    print("📊 WORLD CUP 2026 STATS VIEWER")
    print("=" * 60)
    
    # Find all stats files
    stats_files = glob.glob("data/output/worldcup_analysis_*_stats.json")
    
    if not stats_files:
        print("\nNo stats files found. Run worldcup_analysis.py first!")
        return
    
    print(f"\nFound {len(stats_files)} stats files:")
    for i, f in enumerate(stats_files):
        size = os.path.getsize(f) / 1024
        print(f"  {i+1}. {os.path.basename(f)} ({size:.1f} KB)")
    
    # Let user choose
    choice = input("\nSelect stats file number (or 'q' to quit): ")
    if choice.lower() == 'q':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(stats_files):
            with open(stats_files[idx], 'r') as f:
                stats = json.load(f)
            
            print("\n" + "=" * 60)
            print("📊 MATCH STATISTICS")
            print("=" * 60)
            print(f"Total frames analyzed: {stats.get('total_frames', 0)}")
            
            possession = stats.get('possession', {})
            if possession:
                total = possession.get('Team A', 0) + possession.get('Team B', 0)
                if total > 0:
                    poss_a = possession['Team A'] / total * 100
                    poss_b = possession['Team B'] / total * 100
                    print(f"\n⏱️ Possession:")
                    print(f"   Team A: {poss_a:.1f}%")
                    print(f"   Team B: {poss_b:.1f}%")
            
            print(f"\n⚽ Goals:")
            print(f"   Team A: {stats.get('goals', {}).get('Team A', 0)}")
            print(f"   Team B: {stats.get('goals', {}).get('Team B', 0)}")
            
            print(f"\n🟨 Yellow Cards: {stats.get('yellow_cards', 0)}")
            print(f"🟥 Red Cards: {stats.get('red_cards', 0)}")
            print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_stats()
