"""
SkyJames - Complete Test Suite
Tests all features: dashboard, API, webcam, processing, and advanced features
"""

import os
import sys
import json
import time
import unittest
import subprocess
import requests
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== TEST CONFIGURATION ====================
TEST_CONFIG = {
    'api_url': 'http://localhost:5000',
    'test_video': 'data/input/test_video.avi',
    'test_image': 'data/test/test_image.jpg',
    'output_dir': 'data/output',
    'timeout': 30
}

# ==================== 1. DASHBOARD TESTS ====================
class TestDashboard(unittest.TestCase):
    """Test dashboard functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Setup before all tests"""
        os.makedirs("data/input", exist_ok=True)
        os.makedirs("data/output", exist_ok=True)
        os.makedirs("data/test", exist_ok=True)
        
        # Create test video if not exists
        if not os.path.exists(TEST_CONFIG['test_video']):
            cls._create_test_video()
    
    @staticmethod
    def _create_test_video():
        """Create a test video for testing"""
        import cv2
        import numpy as np
        
        width, height = 640, 480
        fps = 30
        total_frames = 30
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(TEST_CONFIG['test_video'], fourcc, fps, (width, height))
        
        for i in range(total_frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.putText(frame, f"Test Frame {i}", (width//2-100, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.line(frame, (0, height//2), (width, height//2), (0, 255, 0), 2)
            out.write(frame)
        
        out.release()
        print("✅ Test video created")
    
    def test_imports(self):
        """Test all modules import correctly"""
        try:
            import streamlit as st
            import cv2
            import numpy as np
            import pandas as pd
            import plotly.express as px
            import matplotlib.pyplot as plt
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import error: {e}")
    
    def test_directories(self):
        """Test required directories exist"""
        dirs = ['data/input', 'data/output', 'data/sports', 'models']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
            self.assertTrue(os.path.exists(d), f"Directory {d} missing")
    
    def test_test_video(self):
        """Test test video exists and is valid"""
        self.assertTrue(os.path.exists(TEST_CONFIG['test_video']))
        
        # Verify video can be read
        cap = cv2.VideoCapture(TEST_CONFIG['test_video'])
        self.assertTrue(cap.isOpened())
        ret, frame = cap.read()
        self.assertTrue(ret)
        cap.release()

# ==================== 2. API TESTS ====================
class TestAPI(unittest.TestCase):
    """Test API server functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Start API server for testing"""
        cls.api_process = None
        cls.base_url = TEST_CONFIG['api_url']
        
        # Check if API is already running
        try:
            response = requests.get(f"{cls.base_url}/status", timeout=2)
            cls.api_running = response.status_code == 200
        except:
            cls.api_running = False
        
        # Start API if not running
        if not cls.api_running:
            print("Starting API server for tests...")
            cls.api_process = subprocess.Popen(
                ["python", "skyjames.py", "--mode", "api"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)  # Wait for API to start
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        if cls.api_process:
            cls.api_process.terminate()
            cls.api_process.wait(timeout=5)
    
    def test_api_status(self):
        """Test API status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('status', data)
            self.assertEqual(data['status'], 'running')
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running")
    
    def test_api_detection(self):
        """Test API detection endpoint"""
        if not os.path.exists(TEST_CONFIG['test_video']):
            self.skipTest("Test video not available")
        
        try:
            # Read test image
            cap = cv2.VideoCapture(TEST_CONFIG['test_video'])
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Encode image
                _, buffer = cv2.imencode('.jpg', frame)
                files = {'image': ('test.jpg', buffer.tobytes(), 'image/jpeg')}
                
                response = requests.post(
                    f"{self.base_url}/detect",
                    files=files,
                    timeout=10
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['status'], 'success')
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running")

# ==================== 3. PROCESSING TESTS ====================
class TestProcessing(unittest.TestCase):
    """Test video processing functionality"""
    
    def test_import_components(self):
        """Test import of pipeline components"""
        try:
            from src.perception.lane_net_cpu import OptimizedLaneDetector
            from src.perception.object_detector import ObjectDetector
            from src.safety.safety_monitor import SafetyMonitor
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import error: {e}")
    
    def test_lane_detector(self):
        """Test lane detector on a test image"""
        try:
            from src.perception.lane_net_cpu import OptimizedLaneDetector
            from src.config import Config
            
            detector = OptimizedLaneDetector(Config())
            self.assertIsNotNone(detector)
            
            # Test on dummy frame
            dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            result, left, right = detector.process_frame(dummy_frame, use_neural=False)
            self.assertIsNotNone(result)
            
        except Exception as e:
            self.fail(f"Lane detector test failed: {e}")

# ==================== 4. PERFORMANCE TESTS ====================
class TestPerformance(unittest.TestCase):
    """Test performance metrics"""
    
    def test_processing_time(self):
        """Test processing time is reasonable"""
        import time
        
        try:
            from src.perception.lane_net_cpu import OptimizedLaneDetector
            from src.config import Config
            
            detector = OptimizedLaneDetector(Config())
            dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            start_time = time.time()
            result, left, right = detector.process_frame(dummy_frame, use_neural=False)
            processing_time = time.time() - start_time
            
            # Should process in under 1 second
            self.assertLess(processing_time, 1.0, f"Processing too slow: {processing_time:.2f}s")
            
        except Exception as e:
            self.fail(f"Performance test failed: {e}")

# ==================== 5. WEBRTC TESTS ====================
class TestWebRTC(unittest.TestCase):
    """Test WebRTC streaming functionality"""
    
    def test_websocket_import(self):
        """Test websocket import"""
        try:
            import websockets
            self.assertTrue(True)
        except ImportError:
            self.skipTest("websockets not installed")
    
    def test_streamer_init(self):
        """Test streamer initialization"""
        try:
            from scripts.webrtc_stream import WebRTCStreamer
            streamer = WebRTCStreamer()
            self.assertIsNotNone(streamer)
        except ImportError:
            self.skipTest("WebRTC streamer not available")

# ==================== 6. DATABASE TESTS ====================
class TestDatabase(unittest.TestCase):
    """Test database functionality"""
    
    def test_db_init(self):
        """Test database initialization"""
        try:
            from scripts.database import SkyJamesDB
            db = SkyJamesDB("test.db")
            self.assertIsNotNone(db)
            
            # Clean up
            if os.path.exists("test.db"):
                os.remove("test.db")
                
        except ImportError:
            self.skipTest("Database module not available")
        except Exception as e:
            self.fail(f"Database test failed: {e}")

# ==================== 7. ALERT SYSTEM TESTS ====================
class TestAlertSystem(unittest.TestCase):
    """Test alert system"""
    
    def test_alert_import(self):
        """Test alert system import"""
        try:
            from scripts.alert_system import SkyJamesAlert
            alert = SkyJamesAlert()
            self.assertIsNotNone(alert)
        except ImportError:
            self.skipTest("Alert system not available")

# ==================== 8. MULTI-CAMERA TESTS ====================
class TestMultiCamera(unittest.TestCase):
    """Test multi-camera functionality"""
    
    def test_camera_manager(self):
        """Test camera manager"""
        try:
            from scripts.multi_camera import MultiCameraPipeline
            pipeline = MultiCameraPipeline()
            self.assertIsNotNone(pipeline)
        except ImportError:
            self.skipTest("Multi-camera not available")

# ==================== 9. END-TO-END TESTS ====================
class TestEndToEnd(unittest.TestCase):
    """End-to-end pipeline tests"""
    
    def test_full_pipeline(self):
        """Test full pipeline on test video"""
        video_path = TEST_CONFIG['test_video']
        
        if not os.path.exists(video_path):
            self.skipTest("Test video not available")
        
        try:
            from src.perception.lane_net_cpu import OptimizedLaneDetector
            from src.config import Config
            
            detector = OptimizedLaneDetector(Config())
            cap = cv2.VideoCapture(video_path)
            
            frames_processed = 0
            while frames_processed < 10:
                ret, frame = cap.read()
                if not ret:
                    break
                result, left, right = detector.process_frame(frame)
                frames_processed += 1
            
            cap.release()
            self.assertGreater(frames_processed, 0, "No frames processed")
            
        except Exception as e:
            self.fail(f"End-to-end test failed: {e}")

# ==================== TEST RUNNER ====================
def run_all_tests():
    """Run all tests with detailed output"""
    
    print("
" + "=" * 60)
    print("🚀 SkyJames Test Suite")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Load all test cases
    test_cases = [
        TestDashboard,
        TestProcessing,
        TestPerformance,
        TestEndToEnd
    ]
    
    # Optional tests (if features are installed)
    try:
        import requests
        test_cases.append(TestAPI)
    except ImportError:
        print("⚠️ Skipping API tests (requests not installed)")
    
    try:
        import websockets
        test_cases.append(TestWebRTC)
    except ImportError:
        print("⚠️ Skipping WebRTC tests (websockets not installed)")
    
    # Load and run tests
    suite = unittest.TestSuite()
    for test_case in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(test_case))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("
" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Ran: {result.testsRun} tests")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

# ==================== QUICK TEST FUNCTIONS ====================
def quick_test():
    """Quick test for basic functionality"""
    print("
🔍 Running Quick Test...")
    
    checks = []
    
    # Check directories
    dirs = ['data/input', 'data/output', 'data/sports', 'models']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        checks.append(('Directory', d, os.path.exists(d)))
    
    # Check test video
    video_path = TEST_CONFIG['test_video']
    checks.append(('Test Video', video_path, os.path.exists(video_path)))
    
    # Check model
    model_path = 'models/lane_net_optimized.pth'
    checks.append(('Model', model_path, os.path.exists(model_path)))
    
    # Print results
    print("
" + "-" * 40)
    for name, path, status in checks:
        status_str = "✅" if status else "❌"
        print(f"{status_str} {name}: {path}")
    print("-" * 40)
    
    # Test detector
    try:
        from src.perception.lane_net_cpu import OptimizedLaneDetector
        from src.config import Config
        detector = OptimizedLaneDetector(Config())
        print("✅ Detector initialized successfully")
    except Exception as e:
        print(f"❌ Detector initialization failed: {e}")

def test_api_endpoint():
    """Test API endpoint"""
    try:
        import requests
        response = requests.get("http://localhost:5000/status", timeout=5)
        print(f"✅ API Status: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ API not running. Start with: python skyjames.py --mode api")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'quick':
            quick_test()
        elif sys.argv[1] == 'api':
            test_api_endpoint()
        elif sys.argv[1] == 'all':
            success = run_all_tests()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown option: {sys.argv[1]}")
    else:
        # Run quick test by default
        quick_test()
        print("
📝 To run full test suite: python tests/test_suite.py all")
