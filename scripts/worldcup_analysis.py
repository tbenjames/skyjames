"""
Advanced World Cup 2026 Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import json
import time
from collections import defaultdict
from football_analysis import FootballAnalyzer

class WorldCupAnalyzer(FootballAnalyzer):
    def __init__(self):
        super().__init__()
        self.match_stats = {
            'possession': {'Team A': 0, 'Team B': 0},
            'shots_on_target': {'Team A': 0, 'Team B': 0},
            'goals': {'Team A': 0, 'Team B': 0},
            'yellow_cards': 0,
            'red_cards': 0,
            'total_frames': 0
        }
        self.player_positions = defaultdict(list)
        
    def analyze_frame(self, frame):
        """Enhanced World Cup analysis"""
        annotated, stats = super().analyze_frame(frame)
        
        # Track possession
        if stats.get('possession') in ['Team A', 'Team B']:
            self.match_stats['possession'][stats['possession']] += 1
            self.match_stats['total_frames'] += 1
        
        # Detect events (simplified)
        self._detect_events(annotated)
        
        # Add World Cup overlay
        self._add_worldcup_overlay(annotated)
        
        return annotated, stats
    
    def _detect_events(self, frame):
        """Detect key events in World Cup match"""
        # Placeholder for event detection
        # In production, implement:
        # - Goal detection (ball crossing goal line)
        # - Yellow/Red card detection
        # - Substitution detection
        pass
    
    def _add_worldcup_overlay(self, frame):
        """Add World Cup 2026 overlay"""
        h, w = frame.shape[:2]
        
        # World Cup banner
        cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 255), -1)
        cv2.putText(frame, "🏆 FIFA WORLD CUP 2026", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Stats overlay
        if self.match_stats['total_frames'] > 0:
            poss_a = self.match_stats['possession']['Team A'] / self.match_stats['total_frames'] * 100
            poss_b = self.match_stats['possession']['Team B'] / self.match_stats['total_frames'] * 100
            
            cv2.putText(frame, f"Possession: {poss_a:.0f}% - {poss_b:.0f}%", 
                       (w-250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def analyze_worldcup_video(video_path):
    """Analyze a World Cup video"""
    print(f"🏆 Analyzing World Cup 2026: {video_path}")
    
    analyzer = WorldCupAnalyzer()
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_path = f"data/output/worldcup_analysis_{int(time.time())}.mp4"
    os.makedirs("data/output", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Output: {output_path}")
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        annotated, stats = analyzer.analyze_frame(frame)
        out.write(annotated)
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Processed: {frame_count} frames")
    
    cap.release()
    out.release()
    print(f"✅ World Cup analysis complete! Output: {output_path}")
    
    # Save match stats
    stats_path = output_path.replace('.mp4', '_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(analyzer.match_stats, f, indent=2)
    print(f"📊 Stats saved: {stats_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_worldcup_video(sys.argv[1])
    else:
        print("Usage: python worldcup_analysis.py <worldcup_video.mp4>")
        print("\nTrying to find a video automatically...")
        
        # Try to find a video
        video_paths = [
            "data/worldcup/match_highlights.mp4",
            "data/input/test_video.avi",
            "data/input/synthetic_road.mp4"
        ]
        
        for path in video_paths:
            if os.path.exists(path):
                print(f"Found: {path}")
                analyze_worldcup_video(path)
                break
        else:
            print("No video found. Please provide a video path.")
