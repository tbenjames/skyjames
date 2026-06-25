"""
Complete Production Pipeline with all features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import time
import argparse
from tqdm import tqdm
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.perception.object_detector import ObjectDetector
from src.safety.safety_monitor import SafetyMonitor
from src.config import Config

def process_video(video_path, output_path=None, use_neural=True, 
                  object_detection=True, show_progress=True):
    """Process a video with the full pipeline"""
    
    config = Config()
    
    # Load model
    model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    if use_neural and os.path.exists(model_path):
        print(f"✓ Using neural network model: {model_path}")
    else:
        print("⚠ Using traditional method")
        model_path = None
    
    # Initialize components
    detector = OptimizedLaneDetector(config, model_path=model_path)
    object_detector = ObjectDetector(config) if object_detection else None
    safety_monitor = SafetyMonitor(config)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 150
    
    # Setup output
    if output_path is None:
        timestamp = int(time.time())
        output_path = f"data/output/processed_{timestamp}.mp4"
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"\nProcessing: {os.path.basename(video_path)}")
    print(f"Output: {output_path}")
    print(f"Frames: {total_frames} | FPS: {fps} | Size: {width}x{height}")
    print(f"Neural: {'ON' if use_neural else 'OFF'} | Object Detection: {'ON' if object_detection else 'OFF'}")
    print("=" * 60)
    
    progress_bar = tqdm(total=total_frames) if show_progress else None
    frame_count = 0
    safety_violations = 0
    total_time = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        start_time = time.time()
        
        # 1. Lane Detection
        result, left, right = detector.process_frame(frame, use_neural=use_neural)
        
        # 2. Object Detection (every 5 frames)
        if object_detector and frame_count % 5 == 0:
            detections = object_detector.detect_objects(result)
            result = object_detector.draw_detections(result, detections)
        else:
            detections = []
        
        # 3. Safety Check
        perception_result = {'detections': detections, 'lane_lines': (left, right)}
        is_safe, violations = safety_monitor.evaluate_safety(perception_result, {}, {}, None)
        
        if not is_safe:
            safety_violations += 1
        
        # 4. Overlay Information
        elapsed = time.time() - start_time
        total_time += elapsed
        fps_display = 1.0 / elapsed if elapsed > 0 else 0
        
        cv2.putText(result, f"FPS: {fps_display:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(result, f"Frame: {frame_count}", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        status_color = (0, 255, 0) if is_safe else (0, 0, 255)
        cv2.putText(result, f"SAFETY: {'SAFE' if is_safe else 'UNSAFE'}", 
                   (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        lane_status = "BOTH" if (left is not None and right is not None) else \
                     "LEFT" if left is not None else \
                     "RIGHT" if right is not None else "NONE"
        cv2.putText(result, f"Lanes: {lane_status}", (10, 105), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(result, f"Objects: {len(detections)}", (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        out.write(result)
        frame_count += 1
        
        if progress_bar:
            progress_bar.update(1)
            progress_bar.set_postfix({
                'FPS': f'{fps_display:.1f}',
                'Lanes': lane_status
            })
    
    cap.release()
    out.release()
    if progress_bar:
        progress_bar.close()
    
    avg_fps = frame_count / total_time if total_time > 0 else 0
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Frames processed: {frame_count}")
    print(f"Average FPS: {avg_fps:.2f}")
    print(f"Safety violations: {safety_violations}")
    print(f"Safety rate: {((frame_count - safety_violations)/frame_count*100):.1f}%")
    print(f"Output saved to: {output_path}")
    print("=" * 60)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Production Lane Detection Pipeline')
    parser.add_argument('--video', type=str, default='data/input/test_video.avi',
                       help='Path to input video')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to output video')
    parser.add_argument('--no-neural', action='store_true',
                       help='Disable neural network (use traditional)')
    parser.add_argument('--no-obj', action='store_true',
                       help='Disable object detection')
    parser.add_argument('--no-progress', action='store_true',
                       help='Disable progress bar')
    parser.add_argument('--webcam', action='store_true',
                       help='Run webcam mode instead of video')
    
    args = parser.parse_args()
    
    if args.webcam:
        from scripts.webcam_pipeline import main as webcam_main
        webcam_main()
    else:
        process_video(
            video_path=args.video,
            output_path=args.output,
            use_neural=not args.no_neural,
            object_detection=not args.no_obj,
            show_progress=not args.no_progress
        )

if __name__ == "__main__":
    main()
