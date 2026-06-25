"""
SkyJames - Video Summarization (Simplified)
"""

import cv2
import numpy as np
import os
from datetime import datetime

class VideoSummarizer:
    def __init__(self):
        self.keyframes = []
        self.summary = []
    
    def extract_keyframes(self, video_path, num_keyframes=5):
        """Extract keyframes using frame difference"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Could not open video: {video_path}")
            return []
        
        frames = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📹 Processing video: {os.path.basename(video_path)}")
        print(f"   Total frames: {total_frames}")
        
        # Sample frames evenly
        step = max(1, total_frames // num_keyframes)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % step == 0:
                frames.append(frame)
            frame_count += 1
        
        cap.release()
        
        # Select keyframes
        if frames:
            # Select evenly spaced frames
            step = max(1, len(frames) // num_keyframes)
            self.keyframes = frames[::step][:num_keyframes]
            print(f"✅ Extracted {len(self.keyframes)} keyframes")
        
        return self.keyframes
    
    def save_keyframes(self, output_dir="data/keyframes"):
        """Save keyframes to disk"""
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        
        for i, frame in enumerate(self.keyframes):
            path = os.path.join(output_dir, f"keyframe_{i+1}.jpg")
            cv2.imwrite(path, frame)
            saved_paths.append(path)
        
        print(f"💾 Saved {len(saved_paths)} keyframes to {output_dir}")
        return saved_paths
    
    def create_summary_video(self, video_path, output_path=None, duration=5):
        """Create a summary video from keyframes"""
        if not self.keyframes:
            self.extract_keyframes(video_path)
        
        if not self.keyframes:
            return None
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/summary_{timestamp}.avi"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Use first keyframe to get dimensions
        h, w = self.keyframes[0].shape[:2]
        fps = 1  # 1 second per keyframe
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        for frame in self.keyframes:
            out.write(frame)
            # Write multiple times for longer display
            for _ in range(fps * duration // len(self.keyframes)):
                out.write(frame)
        
        out.release()
        print(f"✅ Summary video saved: {output_path}")
        return output_path

# Test function
def test_summarizer():
    print("🚀 Testing Video Summarization...")
    
    summarizer = VideoSummarizer()
    
    # Test on sample video
    video_path = "data/input/test_video.avi"
    if os.path.exists(video_path):
        keyframes = summarizer.extract_keyframes(video_path, num_keyframes=5)
        print(f"📸 Extracted {len(keyframes)} keyframes")
        
        if keyframes:
            saved = summarizer.save_keyframes()
            print(f"💾 Saved keyframes: {saved}")
            
            summary_path = summarizer.create_summary_video(video_path)
            print(f"🎬 Summary video: {summary_path}")
    else:
        print("⚠️ No test video found")
    
    return summarizer

if __name__ == "__main__":
    test_summarizer()
