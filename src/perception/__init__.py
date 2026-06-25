"""
Perception module for autonomous driving
"""

from src.perception.lane_net_cpu import OptimizedLaneDetector, LaneNetCPU
from src.perception.object_detector import ObjectDetector

__all__ = ['OptimizedLaneDetector', 'LaneNetCPU', 'ObjectDetector']
