"""
Real-time lane detection using webcam
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from src.lane_detector import LaneDetector
from src.config import Config
from src.utils import overlay_text

def main():
    # Initialize detector
    detector = LaneDetector()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
    
    print("Press 'q' to quit")
    print("Press 'd' to toggle debug view")
    print("Press 's' to save current frame")
    
    debug_mode = False
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Process frame
        if debug_mode:
            result, edges, masked = detector.process_frame(frame, draw_debug=True)
        else:
            result = detector.process_frame(frame)
        
        # Add overlay text
        result = overlay_text(result, f"Frame: {frame_count}", (10, 30))
        result = overlay_text(result, f"Debug: {'ON' if debug_mode else 'OFF'}", 
                            (10, 60), color=(255, 255, 0) if debug_mode else (0, 255, 0))
        
        # Show result
        cv2.imshow('Lane Detection - Real Time', result)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            debug_mode = not debug_mode
            print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
        elif key == ord('s'):
            timestamp = cv2.getTickCount()
            filename = f"saved_frame_{timestamp}.jpg"
            cv2.imwrite(filename, result)
            print(f"Saved: {filename}")
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
