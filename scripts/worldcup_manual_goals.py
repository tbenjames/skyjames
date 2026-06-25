"""
World Cup 2026 - Portugal vs Uzbekistan
Manual Goal Marking Based on Transcript
Final Score: Portugal 5 - 0 Uzbekistan
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
    def __init__(self, team_a_name="Portugal", team_b_name="Uzbekistan"):
        self.object_detector = ObjectDetector()
        self.team_a_name = team_a_name
        self.team_b_name = team_b_name
        
        # Tracking
        self.tracked_players = defaultdict(lambda: [])
        self.ball_positions = []
        self.ball_trajectory = []
        
        # Match stats
        self.match_stats = {
            'possession': {team_a_name: 0, team_b_name: 0},
            'goals': {team_a_name: 0, team_b_name: 0},
            'goal_events': [],
            'total_frames': 0,
            'possession_frames': 0
        }
        
        # MANUAL GOAL TIMESTAMPS (in seconds) - Based on transcript
        # Goal 1: Ronaldo at 2:00 (120 seconds)
        # Goal 2: Mendes at 4:41 (281 seconds)
        # Goal 3: Ronaldo at 8:44 (524 seconds)
        # Goal 4: Corner at 13:14 (794 seconds)
        # Goal 5: Final at 16:49 (1009 seconds)
        
        self.goal_timestamps = [
            {'time': 120, 'team': team_a_name, 'goal_number': 1, 'scorer': 'Ronaldo'},
            {'time': 281, 'team': team_a_name, 'goal_number': 2, 'scorer': 'Mendes'},
            {'time': 524, 'team': team_a_name, 'goal_number': 3, 'scorer': 'Ronaldo'},
            {'time': 794, 'team': team_a_name, 'goal_number': 4, 'scorer': 'Corner'},
            {'time': 1009, 'team': team_a_name, 'goal_number': 5, 'scorer': 'Final'},
        ]
        
        self.goals_detected = []
        self.frame_count = 0
        self.fps = 30
        
        # Goal display tracking
        self.goals_announced = set()
        
        print(f"🏆 World Cup 2026: {team_a_name} vs {team_b_name}")
        print(f"📊 Manual Score: {team_a_name} 5 - 0 {team_b_name}")
        print(f"⚽ Goals: {len(self.goal_timestamps)} goals expected")
        for goal in self.goal_timestamps:
            print(f"   Goal #{goal['goal_number']}: {goal['scorer']} at {goal['time']//60}:{goal['time']%60:02d}")
        print("=" * 60)
        
    def analyze_frame(self, frame):
        """Analyze a football frame with manual goal marking"""
        
        detections = self.object_detector.detect_objects(frame)
        players = [d for d in detections if d['class_name'] == 'person']
        balls = [d for d in detections if d['class_name'] == 'sports ball']
        
        team_a, team_b = self._classify_teams(frame, players)
        ball_position = self._track_ball(balls)
        
        # Check for goals based on timestamp
        current_time = self.frame_count / self.fps
        self._check_goals(current_time)
        
        # Possession tracking
        if ball_position:
            possession_team = self._determine_possession(ball_position, team_a, team_b)
            if possession_team:
                self.match_stats['possession'][possession_team] += 1
                self.match_stats['possession_frames'] += 1
        
        self._track_players(players)
        stats = self._calculate_stats(team_a, team_b, ball_position)
        stats['goals_detected'] = len(self.goals_detected)
        stats['expected_goals'] = len(self.goal_timestamps)
        
        annotated = self._annotate_frame(frame, team_a, team_b, ball_position, stats)
        
        self.frame_count += 1
        return annotated, stats
    
    def _check_goals(self, current_time):
        """Check if a goal should be marked at this timestamp"""
        for goal in self.goal_timestamps:
            goal_num = goal['goal_number']
            if goal_num not in self.goals_announced:
                time_diff = abs(current_time - goal['time'])
                # If within 1.5 seconds of goal time, mark it
                if time_diff < 1.5:
                    self.match_stats['goal_events'].append({
                        'frame': self.frame_count,
                        'time': current_time,
                        'team': goal['team'],
                        'goal_number': goal_num,
                        'scorer': goal['scorer']
                    })
                    self.match_stats['goals'][goal['team']] += 1
                    self.goals_detected.append(goal_num)
                    self.goals_announced.add(goal_num)
                    print(f"⚽ GOAL #{goal_num}! {goal['scorer']} scores at {current_time:.1f}s (frame {self.frame_count})")
                    print(f"   Score: Portugal {self.match_stats['goals'][self.team_a_name]} - {self.match_stats['goals'][self.team_b_name]} Uzbekistan")
    
    def _classify_teams(self, frame, players):
        team_a = []
        team_b = []
        
        if not players:
            return team_a, team_b
        
        for player in players:
            color = self._extract_jersey_color(frame, player['bbox'])
            if color is not None:
                player['jersey_color'] = color
        
        for player in players:
            if 'jersey_color' in player:
                color = player['jersey_color']
                if color[2] > color[0] and color[2] > 100:
                    team_a.append(player)
                    player['team'] = self.team_a_name
                else:
                    team_b.append(player)
                    player['team'] = self.team_b_name
            else:
                team_a.append(player)
                player['team'] = self.team_a_name
        
        return team_a, team_b
    
    def _extract_jersey_color(self, frame, bbox):
        x1, y1, x2, y2 = bbox
        height = y2 - y1
        
        jersey_y1 = int(y1 + height * 0.2)
        jersey_y2 = int(y1 + height * 0.5)
        
        if jersey_y2 <= jersey_y1:
            return None
        
        jersey_roi = frame[jersey_y1:jersey_y2, x1:x2]
        if jersey_roi.size == 0:
            return None
        
        try:
            pixels = jersey_roi.reshape(-1, 3)
            if len(pixels) == 0:
                return None
            dominant_color = np.mean(pixels, axis=0)
            return dominant_color
        except:
            return None
    
    def _track_ball(self, balls):
        if balls:
            x1, y1, x2, y2 = balls[0]['bbox']
            center = ((x1+x2)//2, (y1+y2)//2)
            self.ball_positions.append(center)
            self.ball_trajectory.append(center)
            
            if len(self.ball_trajectory) > 50:
                self.ball_trajectory = self.ball_trajectory[-50:]
            
            return center
        return None
    
    def _determine_possession(self, ball_position, team_a, team_b):
        if ball_position is None:
            return None
        
        bx, by = ball_position
        
        min_dist_a = float('inf')
        min_dist_b = float('inf')
        
        for player in team_a:
            x1, y1, x2, y2 = player['bbox']
            cx, cy = (x1+x2)//2, (y1+y2)//2
            dist = np.sqrt((bx-cx)**2 + (by-cy)**2)
            min_dist_a = min(min_dist_a, dist)
        
        for player in team_b:
            x1, y1, x2, y2 = player['bbox']
            cx, cy = (x1+x2)//2, (y1+y2)//2
            dist = np.sqrt((bx-cx)**2 + (by-cy)**2)
            min_dist_b = min(min_dist_b, dist)
        
        if min_dist_a < min_dist_b and min_dist_a < 200:
            return self.team_a_name
        elif min_dist_b < min_dist_a and min_dist_b < 200:
            return self.team_b_name
        else:
            return None
    
    def _track_players(self, players):
        for player in players:
            bbox = player['bbox']
            team = player.get('team', 'unknown')
            self.tracked_players[team].append(bbox)
            
            if len(self.tracked_players[team]) > 30:
                self.tracked_players[team] = self.tracked_players[team][-30:]
    
    def _calculate_stats(self, team_a, team_b, ball_position):
        total_poss = self.match_stats['possession_frames']
        poss_a = self.match_stats['possession'][self.team_a_name]
        poss_b = self.match_stats['possession'][self.team_b_name]
        
        poss_a_pct = (poss_a / total_poss * 100) if total_poss > 0 else 0
        poss_b_pct = (poss_b / total_poss * 100) if total_poss > 0 else 0
        
        stats = {
            'team_a_count': len(team_a),
            'team_b_count': len(team_b),
            'total_players': len(team_a) + len(team_b),
            'ball_position': ball_position,
            'ball_tracked': ball_position is not None,
            'frame': self.frame_count,
            'time': self.frame_count / self.fps,
            'possession': f"{self.team_a_name}: {poss_a_pct:.1f}% | {self.team_b_name}: {poss_b_pct:.1f}%",
            'goals': f"{self.team_a_name}: {self.match_stats['goals'][self.team_a_name]} | {self.team_b_name}: {self.match_stats['goals'][self.team_b_name]}",
            'goals_detected': len(self.goals_detected),
            'expected_goals': len(self.goal_timestamps),
            'team_a_name': self.team_a_name,
            'team_b_name': self.team_b_name
        }
        
        return stats
    
    def _annotate_frame(self, frame, team_a, team_b, ball_position, stats):
        result = frame.copy()
        h, w = frame.shape[:2]
        
        # Draw players
        for player in team_a:
            x1, y1, x2, y2 = player['bbox']
            cv2.rectangle(result, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(result, f"{self.team_a_name[:3]}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        for player in team_b:
            x1, y1, x2, y2 = player['bbox']
            cv2.rectangle(result, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(result, f"{self.team_b_name[:3]}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Draw ball
        if ball_position:
            cv2.circle(result, ball_position, 8, (0, 255, 0), -1)
            cv2.putText(result, "BALL", (ball_position[0]-20, ball_position[1]-15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            if len(self.ball_trajectory) > 1:
                for i in range(len(self.ball_trajectory)-1):
                    cv2.line(result, self.ball_trajectory[i], 
                           self.ball_trajectory[i+1], (0, 255, 0), 1)
        
        # BIG SCORE DISPLAY - CENTER TOP
        overlay = result.copy()
        cv2.rectangle(overlay, (w//2 - 220, 10), (w//2 + 220, 80), (0, 0, 0), -1)
        cv2.rectangle(overlay, (w//2 - 220, 10), (w//2 + 220, 80), (255, 255, 255), 2)
        
        # Portugal (Red)
        cv2.putText(overlay, self.team_a_name[:7], (w//2 - 200, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        # Score
        score_text = f"{self.match_stats['goals'][self.team_a_name]} - {self.match_stats['goals'][self.team_b_name]}"
        cv2.putText(overlay, score_text, (w//2 - 35, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
        
        # Uzbekistan (Blue)
        cv2.putText(overlay, self.team_b_name[:7], (w//2 + 80, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        
        # VS
        cv2.putText(overlay, "VS", (w//2 - 65, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Goal progress
        goal_progress = f"⚽ {stats['goals_detected']}/{stats['expected_goals']} goals"
        cv2.putText(overlay, goal_progress, (w//2 - 45, 75),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)
        
        # Stats overlay - Left side
        y_pos = 90
        cv2.rectangle(result, (0, 80), (300, 210), (0, 0, 0), -1)
        cv2.rectangle(result, (0, 80), (300, 210), (255, 255, 255), 1)
        
        cv2.putText(result, "WORLD CUP 2026", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        y_pos += 25
        cv2.putText(result, f"Time: {stats['time']//60:.0f}:{stats['time']%60:02.0f}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        y_pos += 20
        cv2.putText(result, f"{stats['possession']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
        
        y_pos += 20
        cv2.putText(result, f"Players: {stats['team_a_count']} vs {stats['team_b_count']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        
        y_pos += 20
        cv2.putText(result, f"Ball: {'Tracked' if stats['ball_tracked'] else 'Lost'}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        
        # Display recent goal notification
        if self.match_stats['goal_events']:
            last_goal = self.match_stats['goal_events'][-1]
            if last_goal['frame'] > self.frame_count - 60:  # Show for 2 seconds
                goal_text = f"⚽ GOAL! {last_goal['scorer']} scores! ({self.match_stats['goals'][self.team_a_name]}-{self.match_stats['goals'][self.team_b_name]})"
                cv2.putText(result, goal_text, (w//2 - 200, h-50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 3)
        
        return result

def analyze_worldcup_video(video_path):
    """Analyze World Cup video with manual goal marking"""
    
    print("=" * 60)
    print("🏆 WORLD CUP 2026 - PORTUGAL VS UZBEKISTAN")
    print("📊 Manual Score: Portugal 5 - 0 Uzbekistan")
    print("=" * 60)
    
    analyzer = WorldCupAnalyzer("Portugal", "Uzbekistan")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    analyzer.fps = fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    output_path = f"data/output/worldcup_final_{int(time.time())}.mp4"
    os.makedirs("data/output", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"📹 Output: {output_path}")
    print("=" * 60)
    
    progress = tqdm(total=total_frames, desc="Processing")
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        annotated, stats = analyzer.analyze_frame(frame)
        out.write(annotated)
        
        frame_count += 1
        progress.update(1)
        progress.set_postfix({
            'Goals': f"{stats['goals_detected']}/{stats['expected_goals']}",
            'Score': f"{analyzer.match_stats['goals']['Portugal']}-{analyzer.match_stats['goals']['Uzbekistan']}"
        })
    
    cap.release()
    out.release()
    progress.close()
    
    print("\n" + "=" * 60)
    print("🏆 MATCH ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total Frames Processed: {frame_count}")
    print(f"Final Score: Portugal {analyzer.match_stats['goals']['Portugal']} - {analyzer.match_stats['goals']['Uzbekistan']} Uzbekistan")
    print(f"Goals Detected: {len(analyzer.goals_detected)}/{len(analyzer.goal_timestamps)}")
    
    print("\n⚽ GOAL TIMELINE:")
    for goal in analyzer.match_stats['goal_events']:
        print(f"  Goal #{goal['goal_number']}: {goal['scorer']} at {goal['time']:.1f}s (frame {goal['frame']})")
    
    print(f"\n📁 Output: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
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
    
    if video:
        analyze_worldcup_video(video)
    else:
        print("No video found!")
