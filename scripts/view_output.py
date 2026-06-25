"""
View the processed video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import glob

def view_latest_output():
    """View the latest processed video"""
    output_files = glob.glob("data/output/*.mp4")
    
    if not output_files:
        print("No output videos found in data/output/")
        return
    
    # Get the latest file
    latest = max(output_files, key=os.path.getctime)
    print(f"Playing: {latest}")
    
    cap = cv2.VideoCapture(latest)
    if not cap.isOpened():
        print(f"Error opening video: {latest}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imshow('Processed Video', frame)
        
        if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    view_latest_output()
