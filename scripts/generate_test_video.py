"""
Generate a simple test video with lanes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np

def generate_test_video():
    """Generate a simple test video with lane markings"""
    width, height = 640, 480
    fps = 30
    duration = 5  # seconds
    total_frames = fps * duration
    
    output_dir = "data/input"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/test_video.mp4"
    
    # Try different codecs
    codecs = [
        ('mp4v', '.mp4'),
        ('X264', '.mp4'),
        ('MJPG', '.avi'),
        ('XVID', '.avi')
    ]
    
    out = None
    used_codec = None
    
    for codec, ext in codecs:
        try:
            temp_path = output_path if ext == '.mp4' else output_path.replace('.mp4', ext)
            fourcc = cv2.VideoWriter_fourcc(*codec)
            test_out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
            if test_out.isOpened():
                # Test write a frame
                test_frame = np.zeros((height, width, 3), dtype=np.uint8)
                test_out.write(test_frame)
                test_out.release()
                # Re-open properly
                out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
                used_codec = codec
                output_path = temp_path
                print(f"Using codec: {codec}")
                break
        except:
            continue
    
    if out is None or not out.isOpened():
        print("Error: Could not create video writer")
        return None
    
    print(f"Generating test video: {output_path}")
    print(f"Frames: {total_frames}, FPS: {fps}")
    
    for i in range(total_frames):
        # Base frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Road
        cv2.rectangle(frame, (0, height//2), (width, height), (50, 50, 50), -1)
        cv2.rectangle(frame, (0, 0), (width, height//2), (80, 80, 80), -1)
        
        # Animated offset
        offset = int(30 * np.sin(i * 0.03))
        
        # Left lane
        cv2.line(frame, 
                (width//2 - 150 + offset, height), 
                (width//2 - 80 + offset, height//2 + 20),
                (255, 255, 255), 4)
        
        # Right lane
        cv2.line(frame, 
                (width//2 + 150 + offset, height), 
                (width//2 + 80 + offset, height//2 + 20),
                (255, 255, 255), 4)
        
        # Center dashed line
        for y in range(height//2 + 20, height, 40):
            cv2.line(frame,
                    (width//2 + offset, y),
                    (width//2 + offset, y + 20),
                    (255, 255, 255), 3)
        
        # Frame counter
        cv2.putText(frame, f"Frame: {i}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Additional road markings
        cv2.putText(frame, "LANE DETECTION TEST", (width//2 - 100, height//2 - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 200), 1)
        
        out.write(frame)
        
        # Progress
        if i % 30 == 0:
            print(f"  Frame {i}/{total_frames}")
    
    out.release()
    
    # Verify the video was created
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"✓ Test video created: {output_path} ({size} bytes)")
        
        # Test if we can read it back
        test_cap = cv2.VideoCapture(output_path)
        if test_cap.isOpened():
            ret, test_frame = test_cap.read()
            if ret:
                print(f"✓ Video is readable")
            else:
                print(f"⚠ Video created but cannot be read")
            test_cap.release()
        else:
            print(f"⚠ Video created but OpenCV cannot read it")
    else:
        print(f"✗ Failed to create video")
    
    return output_path

if __name__ == "__main__":
    generate_test_video()
