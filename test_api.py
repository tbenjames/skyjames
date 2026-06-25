"""
Test SkyJames API Server
"""

import requests
import json
import base64
from PIL import Image
import io
import cv2
import numpy as np

API_URL = "http://localhost:5001"

def test_status():
    print("1️⃣ Testing /status...")
    response = requests.get(f"{API_URL}/status")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200

def test_health():
    print("\n2️⃣ Testing /health...")
    response = requests.get(f"{API_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200

def test_detect():
    print("\n3️⃣ Testing /detect...")
    # Create a dummy image
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    
    files = {'image': ('test.jpg', buffer.tobytes(), 'image/jpeg')}
    response = requests.post(f"{API_URL}/detect", files=files)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Left lane: {data.get('left_lane')}")
        print(f"   Right lane: {data.get('right_lane')}")
        return True
    else:
        print(f"   Error: {response.text}")
        return False

def test_detect_objects():
    print("\n4️⃣ Testing /detect_objects...")
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    
    files = {'image': ('test.jpg', buffer.tobytes(), 'image/jpeg')}
    response = requests.post(f"{API_URL}/detect_objects", files=files)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Detections: {data.get('count')}")
        return True
    else:
        print(f"   Error: {response.text}")
        return False

def test_process_video():
    print("\n5️⃣ Testing /process_video...")
    # Use test video if exists
    video_path = "data/input/test_video.avi"
    if not os.path.exists(video_path):
        print("   ⚠️ Test video not found, skipping")
        return True
    
    with open(video_path, 'rb') as f:
        files = {'video': ('test_video.avi', f, 'video/x-msvideo')}
        response = requests.post(f"{API_URL}/process_video", files=files)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Processed frames: {data.get('processed_frames')}")
        return True
    else:
        print(f"   Error: {response.text}")
        return False

def main():
    print("=" * 60)
    print("🚀 SkyJames API Test")
    print("=" * 60)
    
    # Test all endpoints
    results = []
    results.append(("Status", test_status()))
    results.append(("Health", test_health()))
    results.append(("Detect", test_detect()))
    results.append(("Detect Objects", test_detect_objects()))
    results.append(("Process Video", test_process_video()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    for name, status in results:
        print(f"  {name}: {'✅' if status else '❌'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
