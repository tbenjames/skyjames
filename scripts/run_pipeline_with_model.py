"""
Run pipeline with trained model
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

def main():
    config = Config()
    
    print("=" * 60)
    print("Pipeline with Trained Model")
    print("=" * 60)
    
    # Check if model exists
    model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    if os.path.exists(model_path):
        print(f"✓ Using trained model: {model_path}")
    else:
        print(f"⚠ Model not found, using traditional method")
        model_path = None
    
    # Initialize components
    print("\nInitializing pipeline...")
    detector = OptimizedLaneDetector(config, model_path=model_path)
    object_detector = ObjectDetector(config)
    safety_monitor = SafetyMonitor(config)
    
    # Find a video
    video_paths = [
        "data/input/test_video.avi",
        "data/input/test_video.mp4",
        "data/input/synthetic_road.mp4",
        "data/input/video.mp4"
    ]
    
    video_path = None
    for path in video_paths:
        if os.path.exists(path):
            video_path = path
            break
    
    if video_path is None:
        print("No video found. Creating test video...")
        from scripts.generate_test_video import generate_test_video
        video_path = generate_test_video()
    
    if video_path is None or not os.path.exists(video_path):
        print(f"Error: No video available")
        return
    
    print(f"\nProcessing video: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 150
    
    os.makedirs("data/output", exist_ok=True)
    output_path = f"data/output/processed_nn_{int(time.time())}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Output: {output_path}")
    print("=" * 60)
    
    progress_bar = tqdm(total=total_frames)
    frame_count = 0
    total_time = 0
    use_neural = model_path is not None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        start_time = time.time()
        
        # Process with neural network
        result, left, right = detector.process_frame(frame, use_neural=use_neural)
        
        # Object detection every 10 frames
        if frame_count % 10 == 0:
            detections = object_detector.detect_objects(result)
            result = object_detector.draw_detections(result, detections)
        else:
            detections = []
        
        # Safety check
        perception_result = {'detections': detections, 'lane_lines': (left, right)}
        is_safe, violations = safety_monitor.evaluate_safety(perception_result, {}, {}, None)
        
        # Overlay info
        elapsed = time.time() - start_time
        total_time += elapsed
        fps_display = 1.0 / elapsed if elapsed > 0 else 0
        
        cv2.putText(result, f"Frame: {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(result, f"FPS: {fps_display:.1f}", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        cv2.putText(result, f"Model: {'NN' if use_neural else 'Trad'}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        status_color = (0, 255, 0) if is_safe else (0, 0, 255)
        cv2.putText(result, f"SAFETY: {'SAFE' if is_safe else 'UNSAFE'}", 
                   (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        lane_status = "BOTH" if (left is not None and right is not None) else \
                     "LEFT" if left is not None else \
                     "RIGHT" if right is not None else "NONE"
        cv2.putText(result, f"Lanes: {lane_status}", (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        out.write(result)
        frame_count += 1
        progress_bar.update(1)
        progress_bar.set_postfix({
            'FPS': f'{fps_display:.1f}',
            'Lanes': lane_status
        })
    
    cap.release()
    out.release()
    progress_bar.close()
    
    avg_fps = frame_count / total_time if total_time > 0 else 0
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Frames: {frame_count}")
    print(f"Average FPS: {avg_fps:.2f}")
    print(f"Model: {'Neural Network' if use_neural else 'Traditional'}")
    print(f"Output: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
