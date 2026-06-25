"""
Generate side-by-side comparison video of traditional vs neural network
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import time
import numpy as np
from tqdm import tqdm
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

def create_comparison_video(video_path, output_path=None, max_frames=300):
    """Create side-by-side comparison video"""
    
    config = Config()
    model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    
    # Initialize detector
    detector = OptimizedLaneDetector(config, model_path=model_path if os.path.exists(model_path) else None)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), max_frames)
    
    # Create output path
    if output_path is None:
        timestamp = int(time.time())
        output_path = f"data/output/comparison_video_{timestamp}.mp4"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Output video (side-by-side: 2x width)
    out_width = width * 2
    out_height = height
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (out_width, out_height))
    
    print(f"\nCreating comparison video: {os.path.basename(video_path)}")
    print(f"Frames: {total_frames} | FPS: {fps}")
    print(f"Output: {output_path}")
    print("=" * 60)
    
    progress = tqdm(total=total_frames, desc="Processing")
    frame_count = 0
    
    while cap.isOpened() and frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process with both methods
        result_trad, _, _ = detector.process_frame(frame, use_neural=False)
        result_nn, _, _ = detector.process_frame(frame, use_neural=True)
        
        # Add labels
        cv2.putText(result_trad, "TRADITIONAL", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(result_nn, "NEURAL NETWORK", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add FPS
        cv2.putText(result_trad, f"Frame: {frame_count}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(result_nn, f"Frame: {frame_count}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Combine side by side
        comparison = np.hstack([result_trad, result_nn])
        
        out.write(comparison)
        
        frame_count += 1
        progress.update(1)
    
    cap.release()
    out.release()
    progress.close()
    
    print(f"\n✅ Comparison video saved: {output_path}")
    return output_path

def main():
    """Main function"""
    
    print("=" * 60)
    print("COMPARISON VIDEO GENERATOR")
    print("=" * 60)
    
    # Find video
    video_paths = [
        "data/real_videos/test_drive.avi",
        "data/real_videos/synthetic_drive.mp4",
        "data/input/test_video.avi",
        "data/input/synthetic_road.mp4"
    ]
    
    video = None
    for path in video_paths:
        if os.path.exists(path):
            video = path
            break
    
    if video is None:
        print("No video found. Creating test video...")
        from scripts.generate_test_video import generate_test_video
        video = generate_test_video()
    
    if video:
        create_comparison_video(video)
    else:
        print("No video available")

if __name__ == "__main__":
    main()
