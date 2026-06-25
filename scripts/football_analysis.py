"""
Football (Soccer) Analysis Pipeline for World Cup
Uses object detection and tracking to analyze matches
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from collections import defaultdict
import time
from tqdm import tqdm
from src.perception.object_detector import ObjectDetector
from src.config import Config

class FootballAnalyzer:
    def __init__(self):
        self.object_detector = ObjectDetector()
        self.tracked_players = defaultdict(lambda: [])
        self.ball_positions = []
        self.frame_count = 0
        self.team_colors = {}
        self.field_lines = []
        
    def analyze_frame(self, frame):
        """
        Analyze a football frame
        """
        # 1. Detect all objects
        detections = self.object_detector.detect_objects(frame)
        
        # 2. Filter football objects
        players = [d for d in detections if d['class_name'] == 'person']
        balls = [d for d in detections if d['class_name'] == 'sports ball']
        
        # 3. Detect field lines
        field_lines = self._detect_field_lines(frame)
        self.field_lines = field_lines
        
        # 4. Classify teams by jersey color
        team_a, team_b = self._classify_teams(frame, players)
        
        # 5. Track players and ball
        tracked_players = self._track_players(players)
        ball_position = self._track_ball(balls)
        
        # 6. Calculate statistics
        stats = self._calculate_stats(team_a, team_b, ball_position)
        
        # 7. Annotate frame
        annotated = self._annotate_frame(frame, team_a, team_b, field_lines, ball_position, stats)
        
        self.frame_count += 1
        return annotated, stats
    
    def _detect_field_lines(self, frame):
        """Detect football field lines"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Hough transform for line detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 
                                minLineLength=200, maxLineGap=50)
        
        if lines is None:
            return []
        
        field_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Filter for horizontal and vertical lines
            if abs(y2 - y1) < 10 or abs(x2 - x1) < 10:
                field_lines.append(line[0])
        
        return field_lines
    
    def _classify_teams(self, frame, players):
        """
        Classify players into two teams based on jersey color
        """
        team_a = []
        team_b = []
        
        if not players:
            return team_a, team_b
        
        # Get jersey colors for all players
        jersey_colors = []
        for player in players:
            color = self._extract_jersey_color(frame, player['bbox'])
            if color is not None:
                jersey_colors.append(color)
                player['jersey_color'] = color
        
        if not jersey_colors:
            return team_a, team_b
        
        # Cluster colors into two teams (simplified)
        colors = np.array(jersey_colors)
        
        # Simple method: split by dominant color
        # In production, use K-means clustering
        mean_color = np.mean(colors, axis=0)
        
        for player in players:
            if 'jersey_color' in player:
                color = player['jersey_color']
                # Compare to mean color
                if np.mean(np.abs(color - mean_color)) < 30:
                    team_a.append(player)
                else:
                    team_b.append(player)
        
        return team_a, team_b
    
    def _extract_jersey_color(self, frame, bbox):
        """Extract jersey color from bounding box"""
        x1, y1, x2, y2 = bbox
        height = y2 - y1
        
        # Sample upper body (jersey area)
        jersey_y1 = int(y1 + height * 0.2)
        jersey_y2 = int(y1 + height * 0.5)
        
        if jersey_y2 <= jersey_y1:
            return None
        
        # Extract region
        jersey_roi = frame[jersey_y1:jersey_y2, x1:x2]
        if jersey_roi.size == 0:
            return None
        
        # Get dominant color
        try:
            # Reshape and find dominant color
            pixels = jersey_roi.reshape(-1, 3)
            if len(pixels) == 0:
                return None
            dominant_color = np.mean(pixels, axis=0)
            return dominant_color
        except:
            return None
    
    def _track_players(self, players):
        """Track players across frames"""
        tracked = []
        for player in players:
            bbox = player['bbox']
            self.tracked_players[player['class_name']].append(bbox)
            tracked.append({
                'position': bbox,
                'id': len(self.tracked_players[player['class_name']]),
                'team': player.get('team', 'unknown')
            })
        
        # Keep recent history
        for key in self.tracked_players:
            if len(self.tracked_players[key]) > 30:
                self.tracked_players[key] = self.tracked_players[key][-30:]
        
        return tracked
    
    def _track_ball(self, balls):
        """Track ball position"""
        if balls:
            x1, y1, x2, y2 = balls[0]['bbox']
            center = ((x1+x2)//2, (y1+y2)//2)
            self.ball_positions.append(center)
            return center
        
        return None
    
    def _calculate_stats(self, team_a, team_b, ball_position):
        """Calculate game statistics"""
        stats = {
            'team_a_players': len(team_a),
            'team_b_players': len(team_b),
            'total_players': len(team_a) + len(team_b),
            'ball_position': ball_position,
            'ball_tracked': ball_position is not None,
            'frame': self.frame_count
        }
        
        # Calculate possession (if ball is tracked)
        if ball_position and len(self.ball_positions) > 10:
            # Simple possession: ball on right = team A, left = team B
            # In production, use more sophisticated method
            half_width = 640 // 2  # Assuming 640x480 video
            if ball_position[0] > half_width:
                stats['possession'] = 'Team A'
            else:
                stats['possession'] = 'Team B'
        else:
            stats['possession'] = 'Unknown'
        
        return stats
    
    def _annotate_frame(self, frame, team_a, team_b, field_lines, ball_position, stats):
        """Annotate frame with football analytics"""
        result = frame.copy()
        
        # Draw field lines
        for line in field_lines:
            x1, y1, x2, y2 = line
            cv2.line(result, (x1, y1), (x2, y2), (255, 255, 0), 2)
        
        # Draw Team A players (Red)
        for player in team_a:
            x1, y1, x2, y2 = player['bbox']
            cv2.rectangle(result, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(result, "A", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Draw Team B players (Blue)
        for player in team_b:
            x1, y1, x2, y2 = player['bbox']
            cv2.rectangle(result, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(result, "B", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Draw ball (Green)
        if ball_position:
            cv2.circle(result, ball_position, 10, (0, 255, 0), -1)
            cv2.putText(result, "BALL", (ball_position[0]-20, ball_position[1]-15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw ball trajectory
            if len(self.ball_positions) > 1:
                for i in range(len(self.ball_positions)-1):
                    cv2.line(result, self.ball_positions[i], 
                           self.ball_positions[i+1], (0, 255, 0), 1)
        
        # Add stats overlay
        y_pos = 30
        cv2.putText(result, f"Frame: {stats['frame']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_pos += 30
        cv2.putText(result, f"Team A: {stats['team_a_players']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        y_pos += 25
        cv2.putText(result, f"Team B: {stats['team_b_players']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        y_pos += 25
        cv2.putText(result, f"Possession: {stats['possession']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        y_pos += 25
        cv2.putText(result, f"Ball: {'Tracked' if stats['ball_tracked'] else 'Lost'}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # World Cup overlay
        cv2.putText(result, "🏆 WORLD CUP ANALYSIS", (result.shape[1]-250, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return result

def main():
    """Main football analysis function"""
    
    print("=" * 60)
    print("🏆 WORLD CUP FOOTBALL ANALYSIS")
    print("=" * 60)
    
    # Find football video
    video_paths = [
        "data/sports/football.mp4",
        "data/sports/world_cup.mp4",
        "data/real_videos/football.mp4",
        "data/input/test_video.avi"
    ]
    
    video_path = None
    for path in video_paths:
        if os.path.exists(path):
            video_path = path
            break
    
    if video_path is None:
        print("\n⚠ No football video found.")
        print("\nPlease add a football video to data/sports/")
        print("Or you can download one using:")
        print("  pip install yt-dlp")
        print("  yt-dlp -f best[ext=mp4] 'https://www.youtube.com/watch?v=VIDEO_ID' -o data/sports/football.mp4")
        return
    
    print(f"\nAnalyzing: {os.path.basename(video_path)}")
    
    # Initialize analyzer
    analyzer = FootballAnalyzer()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Output
    os.makedirs("data/output", exist_ok=True)
    output_path = f"data/output/football_analysis_{int(time.time())}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"\nOutput: {output_path}")
    print(f"Frames: {total_frames}")
    print("=" * 60)
    
    progress = tqdm(total=total_frames)
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Analyze frame
        annotated, stats = analyzer.analyze_frame(frame)
        out.write(annotated)
        
        frame_count += 1
        progress.update(1)
        progress.set_postfix({
            'Players': stats['total_players'],
            'Ball': '✓' if stats['ball_tracked'] else '✗'
        })
    
    cap.release()
    out.release()
    progress.close()
    
    print("\n" + "=" * 60)
    print("✅ FOOTBALL ANALYSIS COMPLETE!")
    print(f"Output saved: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
