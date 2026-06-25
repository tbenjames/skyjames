"""
Real-time football analysis using webcam
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from football_analysis import FootballAnalyzer

def main():
    print("=" * 60)
    print("🏆 FOOTBALL ANALYSIS - WEBCAM MODE")
    print("=" * 60)
    
    analyzer = FootballAnalyzer()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\nPress 'q' to quit")
    print("Press 's' to save screenshot")
    print("=" * 60)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Analyze frame
        annotated, stats = analyzer.analyze_frame(frame)
        
        # Show
        cv2.imshow('Football Analysis - World Cup', annotated)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            timestamp = int(time.time())
            filename = f"data/output/football_screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, annotated)
            print(f"Screenshot saved: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nFootball analysis stopped.")

if __name__ == "__main__":
    main()
