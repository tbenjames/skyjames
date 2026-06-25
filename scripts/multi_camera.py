"""
Multi-camera support for lane detection
"""

import cv2
import threading
from queue import Queue
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

class MultiCameraPipeline:
    def __init__(self):
        self.detector = OptimizedLaneDetector(Config())
        self.cameras = []
        self.queues = {}
        self.results = {}
        
    def add_camera(self, camera_id, source=0):
        """Add a camera to the pipeline"""
        cap = cv2.VideoCapture(source)
        if cap.isOpened():
            self.cameras.append({
                'id': camera_id,
                'cap': cap,
                'thread': None,
                'running': False
            })
            self.queues[camera_id] = Queue(maxsize=10)
            print(f"✅ Camera {camera_id} added")
            return True
        return False
    
    def start(self):
        """Start all camera threads"""
        for cam in self.cameras:
            cam['running'] = True
            cam['thread'] = threading.Thread(
                target=self._process_camera,
                args=(cam,)
            )
            cam['thread'].start()
            print(f"📹 Camera {cam['id']} started")
    
    def _process_camera(self, cam):
        """Process frames from a single camera"""
        cap = cam['cap']
        camera_id = cam['id']
        
        while cam['running']:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Process frame
            result, left, right = self.detector.process_frame(frame)
            
            # Store result
            if not self.queues[camera_id].full():
                self.queues[camera_id].put({
                    'frame': result,
                    'lanes': (left, right)
                })
    
    def get_frame(self, camera_id):
        """Get latest frame from a camera"""
        if camera_id in self.queues and not self.queues[camera_id].empty():
            return self.queues[camera_id].get()
        return None
    
    def stop(self):
        """Stop all cameras"""
        for cam in self.cameras:
            cam['running'] = False
            if cam['thread']:
                cam['thread'].join()
            cam['cap'].release()
        print("🛑 All cameras stopped")

if __name__ == "__main__":
    pipeline = MultiCameraPipeline()
    pipeline.add_camera(0, 0)  # Webcam
    pipeline.start()
    
    try:
        while True:
            frame_data = pipeline.get_frame(0)
            if frame_data:
                cv2.imshow(f"Camera 0", frame_data['frame'])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
