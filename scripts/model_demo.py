"""
SkyJames - Model Demo
Test all integrated models
"""

import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model_manager import load_all_models, model_manager

def test_all_models():
    """Test all loaded models on a sample image"""
    print("=" * 60)
    print("🚀 SkyJames Model Demo")
    print("=" * 60)
    
    # Load all models
    load_all_models()
    
    # Create test image
    print("\n📸 Creating test image...")
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (100, 100), (200, 200), (255, 255, 255), -1)
    cv2.circle(test_img, (400, 300), 50, (255, 255, 255), -1)
    cv2.imwrite("data/test_model.jpg", test_img)
    print("✅ Test image created")
    
    # Test each model
    for model_name in model_manager.active_models:
        print(f"\n📊 Testing: {model_name}")
        print("-" * 40)
        
        try:
            result = model_manager.detect(test_img, model_name)
            if result:
                print(f"   ✅ Success - Found {len(result) if isinstance(result, list) else 1} items")
                
                # Draw and save result
                drawn = model_manager.draw_detections(test_img.copy(), result, 
                                                      model_manager.models[model_name]['type'])
                output_path = f"data/output/{model_name}_result.jpg"
                cv2.imwrite(output_path, drawn)
                print(f"   💾 Saved to: {output_path}")
            else:
                print("   ⚠️ No results")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Demo complete! Check data/output/ for results")
    print("=" * 60)

def test_video(model_name='yolo', video_path=None):
    """Test model on video"""
    if video_path is None:
        video_path = "data/input/test_video.avi"
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    print(f"\n🎬 Testing {model_name} on video...")
    
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_path = f"data/output/{model_name}_video_result.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run detection
        detections = model_manager.detect(frame, model_name)
        drawn = model_manager.draw_detections(frame, detections, 
                                              model_manager.models[model_name]['type'])
        out.write(drawn)
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"   Processed {frame_count} frames")
    
    cap.release()
    out.release()
    print(f"✅ Video saved: {output_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'video':
            model = sys.argv[2] if len(sys.argv) > 2 else 'yolo'
            test_video(model)
        else:
            test_all_models()
    else:
        test_all_models()
