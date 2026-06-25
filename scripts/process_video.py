"""
Script to process a video file
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lane_detector import LaneDetector
from src.config import Config
from src.utils import ensure_directory, get_timestamp

def main():
    # Get video path from command line or use default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "data/input/video.mp4"
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        print("Usage: python process_video.py <video_path>")
        return
    
    # Create output directory
    output_dir = "data/output"
    ensure_directory(output_dir)
    
    # Generate output filename
    timestamp = get_timestamp()
    output_path = f"{output_dir}/processed_{timestamp}.mp4"
    
    # Initialize detector
    detector = LaneDetector()
    
    # Optional: Customize config
    # detector.config.CANNY_LOW = 40
    # detector.config.CANNY_HIGH = 120
    
    # Process video
    print(f"Processing video: {video_path}")
    print(f"Output will be saved to: {output_path}")
    
    detector.process_video(video_path, output_path)
    
    print("Done!")

if __name__ == "__main__":
    main()
