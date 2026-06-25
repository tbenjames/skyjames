"""
SkyJames - Production Computer Vision Pipeline
"""

from src.config import Config
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.perception.object_detector import ObjectDetector
from src.safety.safety_monitor import SafetyMonitor

__version__ = "2.0.0"
__author__ = "SkyJames AI"

__all__ = [
    'Config',
    'OptimizedLaneDetector',
    'ObjectDetector',
    'SafetyMonitor'
]
