"""
SkyJames - Production Computer Vision Pipeline
Configuration settings for autonomous systems
"""

import os
from pathlib import Path

class Config:
    # Project Information
    PROJECT_NAME = "SkyJames"
    PROJECT_VERSION = "2.0.0"
    COMPANY_NAME = "SkyJames AI"
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    CULANE_PATH = "/Users/apple/Downloads/CULane"
    MODEL_DIR = BASE_DIR / "models"
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = DATA_DIR / "output"
    
    # Model paths
    LANE_MODEL_PATH = MODEL_DIR / "lane_net_optimized.pth"
    
    # Training (CPU-optimized)
    BATCH_SIZE = 8
    NUM_EPOCHS = 20
    LEARNING_RATE = 0.001
    IMAGE_SIZE = (128, 256)
    NUM_WORKERS = 0
    
    # Perception
    CANNY_LOW = 50
    CANNY_HIGH = 150
    HOUGH_THRESHOLD = 100
    MIN_LINE_LENGTH = 40
    MAX_LINE_GAP = 100
    ROI_TOP_LEFT = (0.45, 0.65)
    ROI_TOP_RIGHT = (0.55, 0.65)
    ROI_BOTTOM_LEFT = (0.0, 1.0)
    ROI_BOTTOM_RIGHT = (1.0, 1.0)
    
    # Object Detection
    YOLO_MODEL = "yolov8n.pt"
    OBJECT_CONFIDENCE = 0.5
    OBJECT_DEVICE = "cpu"
    
    # Prediction
    HISTORY_LENGTH = 3
    
    # Planning
    ROLLOUT_COUNT = 64
    PLANNING_HORIZON = 20
    WHEELBASE = 2.5
    SPEED_LIMITS = (0.0, 15.0)
    STEERING_LIMITS = (-0.5, 0.5)
    
    # Safety
    MIN_DISTANCE = 3.0
    MAX_STEERING_RATE = 0.5
    MIN_LANE_WIDTH = 2.5
    MAX_SPEED = 15.0
    
    # Colors
    LEFT_LANE_COLOR = (0, 0, 255)
    RIGHT_LANE_COLOR = (255, 0, 0)
    LANE_THICKNESS = 6
    
    # Check if CULane exists
    @property
    def culane_exists(self):
        return os.path.exists(self.CULANE_PATH)
    
    # Create directories
    @classmethod
    def create_directories(cls):
        """Create all necessary directories"""
        dirs = [cls.MODEL_DIR, cls.DATA_DIR, cls.OUTPUT_DIR]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        return cls

# Initialize directories
Config.create_directories()
