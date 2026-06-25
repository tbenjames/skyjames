"""
Run the production pipeline on a video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import time
from tqdm import tqdm
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.perception.object_detector import ObjectDetector
from src.safety.safety_monitor import SafetyMonitor
from src.config import Config

def find_video():
    """Find a video file to process"""
    video_paths = [
        "data/input/test_video.mp4",
        "data/input/test_video.avi",
        "data/input/video.mp4",
        "data/input/synthetic_road.mp4",
        "test_video.mp4",
        "synthetic_road.mp4"
    ]
    
    for path in video_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    config = Config()
    
    print("=" * 60)
    print("Lane Detection Pipeline")
    print("=" * 60)
    
    print("\nInitializing components...")
    detector = OptimizedLaneDetector(config)
    object_detector = ObjectDetector(config)
    safety_monitor = SafetyMonitor(config)
    
    # Find a video
    video_path = find_video()
    
    if video_path is None:
        print("No video found. Creating a test video...")
        try:
            from scripts.generate_test_video import generate_test_video
            video_path = generate_test_video()
        except Exception as e:
            print(f"Error creating test video: {e}")
            return
    
    if video_path is None or not os.path.exists(video_path):
        print(f"Error: No video available")
        return
    
    print(f"\nProcessing video: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        print("Trying to fix video format...")
        
        # Try to convert using different backend
        try:
            # Try with different API preference
            cap = cv2.VideoCapture(video_path, cv2.CAP_ANY)
            if not cap.isOpened():
                print("Still cannot open. Please use a different video format.")
                return
        except:
            return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        fps = 30  # Default
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if width <= 0 or height <= 0:
        print("Error: Invalid video dimensions")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        # Estimate frames
        total_frames = 150  # Default for 5 seconds at 30fps
    
    print(f"Video info: {width}x{height}, {fps}fps, {total_frames} frames")
    
    # Create output
    os.makedirs("data/output", exist_ok=True)
    timestamp = int(time.time())
    output_path = f"data/output/processed_{timestamp}.mp4"
    
    # Use MJPG codec for better compatibility
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        # Try alternative codec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Output: {output_path}")
    print("=" * 60)
    
    progress_bar = tqdm(total=total_frames)
    frame_count = 0
    safety_violations = 0
    total_time = 0
    skipped_frames = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip frames if needed for speed
        if frame_count % 2 == 0:  # Process every 2nd frame for speed
            start_time = time.time()
            
            # Process frame
            try:
                result, left, right = detector.process_frame(frame)
                
                # Object detection (every 10 frames)
                if frame_count % 10 == 0:
                    detections = object_detector.detect_objects(result)
                    result = object_detector.draw_detections(result, detections)
                else:
                    detections = []
                
                # Safety check
                perception_result = {'detections': detections, 'lane_lines': (left, right)}
                is_safe, violations = safety_monitor.evaluate_safety(
                    perception_result, {}, {}, None
                )
                
                if not is_safe:
                    safety_violations += 1
                
                # Overlay status
                elapsed = time.time() - start_time
                total_time += elapsed
                fps_display = 1.0 / elapsed if elapsed > 0 else 0
                
                cv2.putText(result, f"Frame: {frame_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(result, f"FPS: {fps_display:.1f}", (10, 55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                status_color = (0, 255, 0) if is_safe else (0, 0, 255)
                cv2.putText(result, f"SAFETY: {'SAFE' if is_safe else 'UNSAFE'}", 
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                cv2.putText(result, f"Objects: {len(detections)}", (10, 105), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                lane_status = "BOTH" if (left is not None and right is not None) else \
                             "LEFT" if left is not None else \
                             "RIGHT" if right is not None else "NONE"
                cv2.putText(result, f"Lanes: {lane_status}", (10, 130), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                
                out.write(result)
                
                progress_bar.update(1)
                progress_bar.set_postfix({
                    'FPS': f'{fps_display:.1f}',
                    'Safety': 'OK' if is_safe else '!'
                })
                
            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
                skipped_frames += 1
        else:
            skipped_frames += 1
        
        frame_count += 1
        
        # Limit frames for testing
        if frame_count >= 500:  # Process max 500 frames for now
            break
    
    cap.release()
    out.release()
    progress_bar.close()
    
    avg_fps = frame_count / total_time if total_time > 0 else 0
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total frames: {frame_count}")
    print(f"Frames processed: {frame_count - skipped_frames}")
    print(f"Skipped frames: {skipped_frames}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average FPS: {avg_fps:.2f}")
    print(f"Safety violations: {safety_violations}")
    print(f"Safety rate: {((frame_count - safety_violations)/frame_count*100):.1f}%")
    print(f"Output saved to: {output_path}")
    
    return output_path

if __name__ == "__main__":
    main()
