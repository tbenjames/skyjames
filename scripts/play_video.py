"""
Simple video player with controls
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import glob

def play_video(video_path=None):
    """Play a video with keyboard controls"""
    
    if video_path is None:
        # Find latest output
        output_files = glob.glob("data/output/*.mp4")
        if output_files:
            video_path = max(output_files, key=os.path.getctime)
        else:
            print("No videos found")
            return
    
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return
    
    print(f"Playing: {video_path}")
    print("Controls: SPACE=pause, q=quit, r=restart, arrow keys=seek")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        fps = 30
    
    paused = False
    frame_count = 0
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
        
        cv2.putText(frame, f"Frame: {frame_count} | {'PAUSED' if paused else 'PLAYING'}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Video Player', frame)
        
        key = cv2.waitKey(int(1000/fps) if not paused else 10) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
            print(f"{'Paused' if paused else 'Playing'}")
        elif key == ord('r'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_count = 0
            print("Restarted")
        elif key == 81:  # Left arrow
            pos = max(0, cap.get(cv2.CAP_PROP_POS_FRAMES) - 30)
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        elif key == 83:  # Right arrow
            pos = min(cap.get(cv2.CAP_PROP_FRAME_COUNT), 
                     cap.get(cv2.CAP_PROP_POS_FRAMES) + 30)
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Check if a video path was provided
    if len(sys.argv) > 1:
        play_video(sys.argv[1])
    else:
        play_video()
