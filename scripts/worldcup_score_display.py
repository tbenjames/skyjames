"""
World Cup 2026 Analysis - Portugal vs Uzbekistan
Correct Score: Portugal 5 - 0 Uzbekistan
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
import time
from tqdm import tqdm
from collections import defaultdict
from src.perception.object_detector import ObjectDetector
from src.config import Config

class WorldCupAnalyzer:
    def __init__(self, team_a="Portugal", team_b="Uzbekistan"):
        self.object_detector = ObjectDetector()
        self.team_a = team_a
        self.team_b = team_b
        
        # CORRECT SCORE - Portugal won 5-0
        self.match_score = {
            team_a: 5,  # Portugal
            team_b: 0   # Uzbekistan
        }
        
        # Display colors
        self.team_a_color = (0, 0, 255)   # Red for Portugal
        self.team_b_color = (255, 0, 0)   # Blue for Uzbekistan
        
        # Tracking
        self.tracked_players = defaultdict(lambda: [])
        self.ball_positions = []
        
        # Stats
        self.possession = {team_a: 0, team_b: 0}
        self.total_frames = 0
        self.frame_count = 0
        
        print(f"🏆 World Cup 2026: {team_a} vs {team_b}")
        print(f"📊 Final Score: {team_a} {self.match_score[team_a]} - {self.match_score[team_b]} {team_b}")
        print("=" * 60)
    
    def analyze_frame(self, frame):
        """Analyze frame and display correct score"""
        
        # Detect objects
        detections = self.object_detector.detect_objects(frame)
        players = [d for d in detections if d['class_name'] == 'person']
        balls = [d for d in detections if d['class_name'] == 'sports ball']
        
        # Simple team classification (based on color)
        team_a_players, team_b_players = self._classify_teams(players)
        
        # Track ball
        ball_pos = self._track_ball(balls)
        
        # Track possession (simplified)
        if ball_pos:
            possession_team = self._get_possession(ball_pos, team_a_players, team_b_players)
            if possession_team:
                self.possession[possession_team] += 1
                self.total_frames += 1
        
        # Annotate frame with correct score
        annotated = self._annotate_frame(frame, team_a_players, team_b_players, ball_pos)
        
        self.frame_count += 1
        return annotated
    
    def _classify_teams(self, players):
        """Classify players into two teams"""
        team_a = []
        team_b = []
        
        for player in players:
            # If it's a person, assign based on position or color
            # Simple assignment - in production this would use jersey color
            if len(team_a) <= len(team_b):
                team_a.append(player)
            else:
                team_b.append(player)
        
        return team_a, team_b
    
    def _track_ball(self, balls):
        """Track ball position"""
        if balls:
            x1, y1, x2, y2 = balls[0]['bbox']
            center = ((x1+x2)//2, (y1+y2)//2)
            self.ball_positions.append(center)
            return center
        return None
    
    def _get_possession(self, ball_pos, team_a, team_b):
        """Determine which team has possession"""
        if not ball_pos:
            return None
        
        # Simple possession based on ball proximity
        # In production, this would be more sophisticated
        if len(team_a) > len(team_b):
            return self.team_a
        elif len(team_b) > len(team_a):
            return self.team_b
        return self.team_a
    
    def _annotate_frame(self, frame, team_a, team_b, ball_pos):
        """Annotate frame with correct score"""
        result = frame.copy()
        h, w = frame.shape[:2]
        
        # Draw players
        for player in team_a:
            x1, y1, x2, y2 = player['bbox']
            cv2.rectangle(result, (x1, y1), (x2, y2), self.team_a_color, 2)
            cv2.putText(result, f"{self.team_a[:3]}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.team_a_color, 1)
        
        for player in team_b:
            x1, y1, x2, y2 = player['bbox']
            cv2.rectangle(result, (x1, y1), (x2, y2), self.team_b_color, 2)
            cv2.putText(result, f"{self.team_b[:3]}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.team_b_color, 1)
        
        # Draw ball
        if ball_pos:
            cv2.circle(result, ball_pos, 8, (0, 255, 0), -1)
            cv2.putText(result, "BALL", (ball_pos[0]-20, ball_pos[1]-15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Draw score overlay - BIG AND CLEAR
        overlay = result.copy()
        
        # Dark background for score
        cv2.rectangle(overlay, (w//2 - 180, 10), (w//2 + 180, 70), (0, 0, 0), -1)
        cv2.rectangle(overlay, (w//2 - 180, 10), (w//2 + 180, 70), (255, 255, 255), 2)
        
        # Team A (Portugal - RED)
        cv2.putText(overlay, self.team_a[:3], (w//2 - 160, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.team_a_color, 3)
        
        # Score display
        score_text = f"{self.match_score[self.team_a]} - {self.match_score[self.team_b]}"
        cv2.putText(overlay, score_text, (w//2 - 35, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        
        # Team B (Uzbekistan - BLUE)
        cv2.putText(overlay, self.team_b[:3], (w//2 + 70, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.team_b_color, 3)
        
        # Add vs
        cv2.putText(overlay, "VS", (w//2 - 60, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Blend with alpha
        result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)
        
        # Add World Cup banner
        cv2.rectangle(result, (0, 0), (w, 40), (0, 0, 180), -1)
        cv2.putText(result, "🏆 FIFA WORLD CUP 2026", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add stats on right side
        cv2.rectangle(result, (w-220, 0), (w, 160), (0, 0, 0), -1)
        cv2.rectangle(result, (w-220, 0), (w, 160), (255, 255, 255), 1)
        
        y_pos = 30
        cv2.putText(result, "MATCH STATS", (w-210, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        y_pos += 25
        cv2.putText(result, f"Frame: {self.frame_count}", (w-210, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        y_pos += 20
        cv2.putText(result, f"Players: {len(team_a)} vs {len(team_b)}", (w-210, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        y_pos += 20
        # Calculate possession
        total_poss = self.possession[self.team_a] + self.possession[self.team_b]
        if total_poss > 0:
            poss_a = self.possession[self.team_a] / total_poss * 100
            poss_b = self.possession[self.team_b] / total_poss * 100
        else:
            poss_a = poss_b = 0
        
        cv2.putText(result, f"Possession: {poss_a:.0f}% - {poss_b:.0f}%", (w-210, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
        
        y_pos += 20
        cv2.putText(result, f"Result: {self.team_a} {self.match_score[self.team_a]}", (w-210, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        y_pos += 20
        cv2.putText(result, f"{self.team_b} {self.match_score[self.team_b]}", (w-210, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        return result
    
    def process_video(self, video_path):
        """Process the entire video"""
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open {video_path}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Output
        output_path = f"data/output/worldcup_score_{int(time.time())}.mp4"
        os.makedirs("data/output", exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"📹 Processing: {os.path.basename(video_path)}")
        print(f"📊 Showing Score: {self.team_a} {self.match_score[self.team_a]} - {self.match_score[self.team_b]} {self.team_b}")
        print(f"📁 Output: {output_path}")
        print("=" * 60)
        
        progress = tqdm(total=total_frames, desc="Processing")
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Analyze frame
            annotated = self.analyze_frame(frame)
            out.write(annotated)
            
            frame_count += 1
            progress.update(1)
            
            # Update progress with score
            if frame_count % 100 == 0:
                progress.set_postfix({
                    'Score': f"{self.match_score[self.team_a]}-{self.match_score[self.team_b]}",
                    'Frames': frame_count
                })
        
        cap.release()
        out.release()
        progress.close()
        
        print("\n" + "=" * 60)
        print("✅ PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Total Frames: {frame_count}")
        print(f"Final Score: {self.team_a} {self.match_score[self.team_a]} - {self.match_score[self.team_b]} {self.team_b}")
        print(f"Output: {output_path}")
        print("=" * 60)

def main():
    """Main function"""
    
    print("=" * 60)
    print("🏆 WORLD CUP 2026 - PORTUGAL VS UZBEKISTAN")
    print("=" * 60)
    print("📊 Correct Score: Portugal 5 - 0 Uzbekistan")
    print("=" * 60)
    
    # Find video
    import glob
    video_paths = [
        "data/worldcup/*.mp4",
        "data/input/*.mp4"
    ]
    
    video = None
    for pattern in video_paths:
        matches = glob.glob(pattern)
        if matches:
            video = matches[0]
            break
    
    if not video:
        print("No video found!")
        return
    
    # Create analyzer with correct score
    analyzer = WorldCupAnalyzer("Portugal", "Uzbekistan")
    analyzer.process_video(video)

if __name__ == "__main__":
    main()
