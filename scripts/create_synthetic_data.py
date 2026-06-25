"""
Create a synthetic video for testing lane detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from src.utils import ensure_directory

def create_synthetic_video():
    """Create synthetic road video with lane markings"""
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    total_frames = fps * duration
    
    # Output directory
    output_dir = "data/input"
    ensure_directory(output_dir)
    output_path = f"{output_dir}/synthetic_road.mp4"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for i in range(total_frames):
        # Create base frame (dark road)
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add road (dark gray)
        cv2.rectangle(frame, (0, height//2), (width, height), (50, 50, 50), -1)
        cv2.rectangle(frame, (0, 0), (width, height//2), (100, 100, 100), -1)
        
        # Animate lane positions (slight curve)
        offset = int(30 * np.sin(i * 0.02))
        
        # Left lane (white line)
        cv2.line(frame, 
                (width//2 - 150 + offset, height), 
                (width//2 - 80 + offset, height//2 + 20),
                (255, 255, 255), 4)
        
        # Right lane (white line)
        cv2.line(frame, 
                (width//2 + 150 + offset, height), 
                (width//2 + 80 + offset, height//2 + 20),
                (255, 255, 255), 4)
        
        # Center dashed line
        for y in range(height//2 + 20, height, 40):
            cv2.line(frame,
                    (width//2 + offset, y),
                    (width//2 + offset, y + 20),
                    (255, 255, 255), 3)
        
        # Add some noise
        noise = np.random.randint(0, 10, (height, width, 3), dtype=np.uint8)
        frame = cv2.add(frame, noise)
        
        # Add timestamp
        cv2.putText(frame, f"Frame: {i}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        out.write(frame)
    
    out.release()
    print(f"Synthetic video created: {output_path}")
    return output_path

def main():
    print("Creating synthetic test video...")
    video_path = create_synthetic_video()
    print("Done! You can now test with: python scripts/process_video.py", video_path)

if __name__ == "__main__":
    main()
