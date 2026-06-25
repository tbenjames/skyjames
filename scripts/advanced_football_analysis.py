"""
Advanced Football Analysis for World Cup 2026
Adds player heat maps, speed calculation, and tactical analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from collections import defaultdict
import json
import time
from tqdm import tqdm

class AdvancedFootballAnalyzer:
    def __init__(self, team_a="Portugal", team_b="Uzbekistan"):
        self.team_a = team_a
        self.team_b = team_b
        
        # Player tracking
        self.player_positions = {team_a: [], team_b: []}
        self.player_speeds = {team_a: [], team_b: []}
        self.heat_maps = {team_a: None, team_b: None}
        
        # Ball tracking
        self.ball_positions = []
        self.ball_speeds = []
        
        # Pass detection
        self.passes = []
        self.current_possession = None
        
        # Match stats
        self.match_stats = {
            'possession': {team_a: 0, team_b: 0},
            'goals': {team_a: 0, team_b: 0},
            'shots_on_target': {team_a: 0, team_b: 0},
            'passes_completed': {team_a: 0, team_b: 0},
            'pass_accuracy': {team_a: 0, team_b: 0}
        }
        
        # Player tracking
        self.tracked_players = {}
        self.next_player_id = 0
        
        # Frame dimensions
        self.frame_count = 0
        self.fps = 30
        self.pixels_per_meter = 10  # Approximate conversion
        
        # Goal area
        self.goal_areas = {
            'left': {'x1': 0, 'x2': 80, 'y1': 200, 'y2': 400},
            'right': {'x1': 560, 'x2': 640, 'y1': 200, 'y2': 400}
        }
        
    def analyze_frame(self, frame, detections):
        """Advanced analysis with player tracking and metrics"""
        
        self.frame_count += 1
        players = [d for d in detections if d['class_name'] == 'person']
        balls = [d for d in detections if d['class_name'] == 'sports ball']
        
        # 1. Track players and calculate positions
        tracked_players = self._track_players(players)
        
        # 2. Update heat maps
        self._update_heat_maps(tracked_players)
        
        # 3. Calculate player speeds
        self._calculate_speeds(tracked_players)
        
        # 4. Track ball and calculate speed
        ball_pos = self._track_ball(balls)
        
        # 5. Detect passes
        if ball_pos:
            self._detect_passes(ball_pos, tracked_players)
        
        # 6. Detect shots on target
        if ball_pos:
            self._detect_shots(ball_pos)
        
        # 7. Calculate possession
        possession_team = self._calculate_possession(ball_pos, tracked_players)
        if possession_team:
            self.match_stats['possession'][possession_team] += 1
        
        # 8. Detect goals
        if ball_pos:
            self._detect_goals(ball_pos)
        
        # 9. Draw advanced annotations
        annotated = self._draw_advanced_annotations(frame, tracked_players, ball_pos)
        
        return annotated
    
    def _track_players(self, players):
        """Track players across frames"""
        tracked = []
        
        for player in players:
            # Simple tracking: assign ID based on proximity to previous positions
            x1, y1, x2, y2 = player['bbox']
            cx, cy = (x1+x2)//2, (y1+y2)//2
            
            # Find closest existing player
            min_dist = float('inf')
            closest_id = None
            
            for pid, history in self.tracked_players.items():
                if history:
                    last_pos = history[-1]['position']
                    dist = np.sqrt((cx - last_pos[0])**2 + (cy - last_pos[1])**2)
                    if dist < 100 and dist < min_dist:  # 100 pixel threshold
                        min_dist = dist
                        closest_id = pid
            
            if closest_id is None:
                closest_id = self.next_player_id
                self.next_player_id += 1
                self.tracked_players[closest_id] = []
            
            # Add position
            self.tracked_players[closest_id].append({
                'position': (cx, cy),
                'bbox': (x1, y1, x2, y2),
                'team': player.get('team', 'unknown'),
                'frame': self.frame_count
            })
            
            tracked.append({
                'id': closest_id,
                'position': (cx, cy),
                'bbox': (x1, y1, x2, y2),
                'team': player.get('team', 'unknown')
            })
        
        return tracked
    
    def _calculate_speeds(self, tracked_players):
        """Calculate player speeds in km/h"""
        for player in tracked_players:
            pid = player['id']
            history = self.tracked_players[pid]
            
            if len(history) >= 2:
                # Calculate speed between last two frames
                prev = history[-2]['position']
                curr = history[-1]['position']
                dist_pixels = np.sqrt((curr[0] - prev[0])**2 + (curr[1] - prev[1])**2)
                dist_meters = dist_pixels / self.pixels_per_meter
                time_seconds = 1.0 / self.fps
                speed_mps = dist_meters / time_seconds
                speed_kmh = speed_mps * 3.6
                
                player['speed'] = speed_kmh
                self.player_speeds[player['team']].append(speed_kmh)
    
    def _update_heat_maps(self, tracked_players):
        """Update player heat maps"""
        for player in tracked_players:
            team = player['team']
            if team in self.player_positions:
                self.player_positions[team].append(player['position'])
        
        # Generate heat maps every 100 frames
        if self.frame_count % 100 == 0:
            for team in [self.team_a, self.team_b]:
                if len(self.player_positions[team]) > 0:
                    self._generate_heat_map(team)
    
    def _generate_heat_map(self, team):
        """Generate heat map for a team"""
        positions = self.player_positions[team]
        if not positions:
            return
        
        # Create heat map
        heat_map = np.zeros((480, 640, 3), dtype=np.uint8)
        
        for pos in positions[-1000:]:  # Last 1000 positions
            x, y = pos
            if 0 <= x < 640 and 0 <= y < 480:
                cv2.circle(heat_map, (int(x), int(y)), 5, (0, 0, 255), -1)
        
        # Apply gaussian blur
        heat_map = cv2.GaussianBlur(heat_map, (51, 51), 0)
        
        # Normalize
        heat_map = cv2.normalize(heat_map, None, 0, 255, cv2.NORM_MINMAX)
        self.heat_maps[team] = heat_map.astype(np.uint8)
    
    def _track_ball(self, balls):
        """Track ball position"""
        if balls:
            x1, y1, x2, y2 = balls[0]['bbox']
            center = ((x1+x2)//2, (y1+y2)//2)
            self.ball_positions.append(center)
            
            # Calculate ball speed
            if len(self.ball_positions) >= 2:
                prev = self.ball_positions[-2]
                curr = self.ball_positions[-1]
                dist_pixels = np.sqrt((curr[0] - prev[0])**2 + (curr[1] - prev[1])**2)
                dist_meters = dist_pixels / self.pixels_per_meter
                time_seconds = 1.0 / self.fps
                speed_mps = dist_meters / time_seconds
                self.ball_speeds.append(speed_mps)
            
            return center
        return None
    
    def _detect_passes(self, ball_pos, tracked_players):
        """Detect ball passes between players"""
        if len(self.ball_positions) < 10:
            return
        
        # Check if ball is moving from one player to another
        # Simplified: track ball ownership changes
        min_dist = float('inf')
        nearest_player = None
        
        for player in tracked_players:
            px, py = player['position']
            dist = np.sqrt((ball_pos[0] - px)**2 + (ball_pos[1] - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest_player = player
        
        if nearest_player and min_dist < 50:
            if self.current_possession != nearest_player['id']:
                # Pass detected
                if self.current_possession is not None:
                    self.passes.append({
                        'from': self.current_possession,
                        'to': nearest_player['id'],
                        'frame': self.frame_count,
                        'team': nearest_player['team']
                    })
                    # Increment pass count
                    self.match_stats['passes_completed'][nearest_player['team']] += 1
                
                self.current_possession = nearest_player['id']
    
    def _detect_shots(self, ball_pos):
        """Detect shots on target"""
        # Check if ball is moving toward goal at high speed
        if len(self.ball_speeds) < 2:
            return
        
        recent_speeds = self.ball_speeds[-5:]
        avg_speed = np.mean(recent_speeds) if recent_speeds else 0
        
        # Shot detection: high speed and moving toward goal
        if avg_speed > 5.0:  # 5 m/s threshold
            x, y = ball_pos
            
            # Check if ball is in goal area or moving toward it
            for goal_side, goal_area in self.goal_areas.items():
                if goal_area['x1'] < x < goal_area['x2'] and goal_area['y1'] < y < goal_area['y2']:
                    # Determine which team shot
                    possession_team = self._get_current_team()
                    if possession_team:
                        self.match_stats['shots_on_target'][possession_team] += 1
                        print(f"💥 Shot on target by {possession_team} at frame {self.frame_count}")
    
    def _get_current_team(self):
        """Get team with current possession"""
        if self.current_possession is not None:
            for pid, history in self.tracked_players.items():
                if pid == self.current_possession and history:
                    return history[-1].get('team', 'unknown')
        return None
    
    def _calculate_possession(self, ball_pos, tracked_players):
        """Calculate which team has possession"""
        if ball_pos is None or not tracked_players:
            return None
        
        # Find nearest player to ball
        min_dist = float('inf')
        nearest_team = None
        
        for player in tracked_players:
            px, py = player['position']
            dist = np.sqrt((ball_pos[0] - px)**2 + (ball_pos[1] - py)**2)
            if dist < min_dist and dist < 150:  # 150 pixel threshold
                min_dist = dist
                nearest_team = player['team']
        
        return nearest_team
    
    def _detect_goals(self, ball_pos):
        """Detect goals"""
        x, y = ball_pos
        
        for goal_side, goal_area in self.goal_areas.items():
            if goal_area['x1'] < x < goal_area['x2'] and goal_area['y1'] < y < goal_area['y2']:
                # Check if ball is in goal area for multiple frames
                # Simplified: goal detected
                if not hasattr(self, '_goal_cooldown') or self._goal_cooldown < self.frame_count - 30:
                    # Determine which team scored
                    possession_team = self._get_current_team()
                    if possession_team:
                        self.match_stats['goals'][possession_team] += 1
                        self._goal_cooldown = self.frame_count
                        print(f"⚽ GOAL! {possession_team} scores at frame {self.frame_count}")
                break
    
    def _draw_advanced_annotations(self, frame, tracked_players, ball_pos):
        """Draw advanced annotations"""
        result = frame.copy()
        
        # Draw team names
        cv2.putText(result, f"{self.team_a} (Red)", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(result, f"{self.team_b} (Blue)", (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw players with IDs and speeds
        for player in tracked_players:
            x1, y1, x2, y2 = player['bbox']
            team = player['team']
            color = (0, 0, 255) if team == self.team_a else (255, 0, 0)
            
            cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
            
            # Player ID and speed
            cv2.putText(result, f"#{player['id']}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            if 'speed' in player:
                cv2.putText(result, f"{player['speed']:.1f}km/h", (x1, y1+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
        
        # Draw ball with trajectory
        if ball_pos:
            cv2.circle(result, ball_pos, 8, (0, 255, 0), -1)
            
            # Draw trajectory
            if len(self.ball_positions) > 1:
                for i in range(1, len(self.ball_positions[-10:])):
                    cv2.line(result, self.ball_positions[-i-1], 
                           self.ball_positions[-i], (0, 255, 0), 1)
        
        # Draw pass network
        if self.passes:
            # Draw pass connections
            pass_count = len(self.passes)
            cv2.putText(result, f"Passes: {pass_count}", (500, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw heat maps (if available)
        if self.heat_maps[self.team_a] is not None:
            # Overlay heat map
            heat = cv2.applyColorMap(self.heat_maps[self.team_a], cv2.COLORMAP_JET)
            result = cv2.addWeighted(result, 0.7, heat, 0.3, 0)
        
        # Draw stats
        stats_y = 90
        cv2.putText(result, f"Goals: {self.match_stats['goals'][self.team_a]} - {self.match_stats['goals'][self.team_b]}", 
                   (10, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        stats_y += 25
        cv2.putText(result, f"Shots on target: {self.match_stats['shots_on_target'][self.team_a]} - {self.match_stats['shots_on_target'][self.team_b]}", 
                   (10, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return result
    
    def get_match_report(self):
        """Generate comprehensive match report"""
        report = {
            'teams': {'team_a': self.team_a, 'team_b': self.team_b},
            'score': {
                self.team_a: self.match_stats['goals'][self.team_a],
                self.team_b: self.match_stats['goals'][self.team_b]
            },
            'possession': {
                self.team_a: self.match_stats['possession'][self.team_a],
                self.team_b: self.match_stats['possession'][self.team_b]
            },
            'shots_on_target': {
                self.team_a: self.match_stats['shots_on_target'][self.team_a],
                self.team_b: self.match_stats['shots_on_target'][self.team_b]
            },
            'passes_completed': {
                self.team_a: self.match_stats['passes_completed'][self.team_a],
                self.team_b: self.match_stats['passes_completed'][self.team_b]
            },
            'total_passes': len(self.passes),
            'total_frames': self.frame_count
        }
        
        return report

# Main function
def main():
    print("="*60)
    print("ADVANCED FOOTBALL ANALYSIS - WORLD CUP 2026")
    print("="*60)
    
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
    
    print(f"Analyzing: {os.path.basename(video)}")
    print("This will take a moment...")
    
    # Run analysis
    analyzer = AdvancedFootballAnalyzer("Portugal", "Uzbekistan")
    
    cap = cv2.VideoCapture(video)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Simulate frame processing (you would integrate with actual detections)
    progress = tqdm(total=min(total_frames, 1000), desc="Processing")
    
    for i in range(min(total_frames, 1000)):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Placeholder: In real implementation, you'd pass actual detections
        # For demo, we'll pass empty detections
        annotated = analyzer.analyze_frame(frame, [])
        
        progress.update(1)
    
    cap.release()
    progress.close()
    
    # Generate report
    report = analyzer.get_match_report()
    print("\n" + "="*60)
    print("MATCH REPORT")
    print("="*60)
    print(f"Final Score: {report['teams']['team_a']} {report['score']['team_a']} - {report['score']['team_b']} {report['teams']['team_b']}")
    print(f"Total Frames: {report['total_frames']}")
    print(f"Total Passes: {report['total_passes']}")
    print(f"Shots on Target: {report['shots_on_target']}")
    
    # Save report
    os.makedirs("data/output", exist_ok=True)
    with open("data/output/advanced_match_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: data/output/advanced_match_report.json")

if __name__ == "__main__":
    main()
