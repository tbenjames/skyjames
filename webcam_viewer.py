"""
SkyJames - Simple Webcam Viewer (No Streamlit)
Run with: python webcam_viewer.py
"""

import cv2
import requests
import base64
import time
import numpy as np
from src.webcam_capture import webcam
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

def main():
    print("📹 SkyJames Webcam Viewer")
    print("=" * 50)
    print("Press 'q' to quit")
    print("Press 's' to save frame")
    print("Press 'r' to record video")
    print("=" * 50)
    
    # Initialize detector
    detector = OptimizedLaneDetector(Config())
    
    # Start webcam
    print("Starting webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    recording = False
    out = None
    frame_count = 0
    fps_display = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame with lane detection
        result, left, right = detector.process_frame(frame)
        
        # Calculate FPS
        frame_count += 1
        elapsed = time.time() - start_time
        if elapsed > 0:
            fps_display = frame_count / elapsed
        
        # Add overlay
        cv2.putText(result, f"SkyJames AI - FPS: {fps_display:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(result, f"Frames: {frame_count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        lane_status = "BOTH" if (left is not None and right is not None) else \
                     "LEFT" if left is not None else \
                     "RIGHT" if right is not None else "NONE"
        cv2.putText(result, f"Lanes: {lane_status}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        if recording:
            cv2.putText(result, "🔴 RECORDING", (result.shape[1] - 150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            out.write(result)
        
        # Show the frame
        cv2.imshow('SkyJames Webcam', result)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            timestamp = int(time.time())
            filename = f"data/output/webcam_capture_{timestamp}.jpg"
            cv2.imwrite(filename, result)
            print(f"📸 Saved: {filename}")
        elif key == ord('r'):
            if recording:
                recording = False
                out.release()
                print("⏹️ Recording stopped")
            else:
                timestamp = int(time.time())
                filename = f"data/output/webcam_record_{timestamp}.avi"
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(filename, fourcc, 30, (640, 480))
                recording = True
                print(f"🔴 Recording started: {filename}")
    
    # Cleanup
    cap.release()
    if recording:
        out.release()
    cv2.destroyAllWindows()
    print("👋 Webcam viewer closed")

if __name__ == "__main__":
    main()
