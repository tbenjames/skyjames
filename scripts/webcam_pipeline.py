"""
Real-time lane detection with webcam using trained model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import time
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.perception.object_detector import ObjectDetector
from src.config import Config

def main():
    config = Config()
    
    print("=" * 60)
    print("Webcam Lane Detection Pipeline")
    print("=" * 60)
    
    # Load model
    model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    if os.path.exists(model_path):
        print(f"✓ Using trained model: {model_path}")
    else:
        print(f"⚠ Model not found, using traditional method")
        model_path = None
    
    # Initialize detector
    detector = OptimizedLaneDetector(config, model_path=model_path)
    object_detector = ObjectDetector(config)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\nPress 'q' to quit")
    print("Press 'd' to toggle debug mode")
    print("Press 'n' to toggle neural network")
    print("=" * 60)
    
    debug_mode = False
    use_neural = model_path is not None
    frame_count = 0
    fps_display = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        start_time = time.time()
        
        # Process frame
        result, left, right = detector.process_frame(frame, use_neural=use_neural)
        
        # Object detection (every 5 frames for speed)
        if frame_count % 5 == 0:
            detections = object_detector.detect_objects(result)
            result = object_detector.draw_detections(result, detections)
        else:
            detections = []
        
        # Calculate FPS
        elapsed = time.time() - start_time
        fps_display = 0.9 * fps_display + 0.1 * (1.0 / elapsed) if frame_count > 0 else 1.0 / elapsed
        
        # Overlay info
        cv2.putText(result, f"FPS: {fps_display:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(result, f"Model: {'NN' if use_neural else 'Trad'}", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        lane_status = "BOTH" if (left is not None and right is not None) else \
                     "LEFT" if left is not None else \
                     "RIGHT" if right is not None else "NONE"
        cv2.putText(result, f"Lanes: {lane_status}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        if debug_mode:
            cv2.putText(result, "DEBUG: ON", (10, 105), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Show the result
        cv2.imshow('Lane Detection - Webcam', result)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            debug_mode = not debug_mode
            print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
        elif key == ord('n'):
            if model_path:
                use_neural = not use_neural
                print(f"Using neural network: {'ON' if use_neural else 'OFF'}")
            else:
                print("No neural network model available")
        elif key == ord('s'):
            timestamp = int(time.time())
            filename = f"data/output/screenshot_{timestamp}.jpg"
            os.makedirs("data/output", exist_ok=True)
            cv2.imwrite(filename, result)
            print(f"Screenshot saved: {filename}")
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nWebcam pipeline stopped.")

if __name__ == "__main__":
    main()
