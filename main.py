#!/usr/bin/env python
"""
Lane Detection System - Main Entry Point
"""

import os
import sys
import argparse
from src.lane_detector import LaneDetector
from src.utils import ensure_directory, get_timestamp

def main():
    parser = argparse.ArgumentParser(description='Lane Detection System')
    parser.add_argument('--video', type=str, help='Path to input video file')
    parser.add_argument('--image', type=str, help='Path to input image file')
    parser.add_argument('--webcam', action='store_true', help='Use webcam for real-time detection')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--synthetic', action='store_true', help='Create synthetic test video')
    
    args = parser.parse_args()
    
    # Handle synthetic data creation
    if args.synthetic:
        from scripts.create_synthetic_data import create_synthetic_video
        create_synthetic_video()
        return
    
    # Handle webcam mode
    if args.webcam:
        from scripts.real_time import main as real_time_main
        real_time_main()
        return
    
    # Handle video processing
    if args.video:
        if not os.path.exists(args.video):
            print(f"Error: Video file not found: {args.video}")
            return
        
        detector = LaneDetector()
        output_path = args.output or f"data/output/processed_{get_timestamp()}.mp4"
        ensure_directory(os.path.dirname(output_path))
        
        detector.process_video(args.video, output_path)
        return
    
    # Handle image processing
    if args.image:
        from scripts.process_image import main as image_main
        # Pass image path as argument
        sys.argv = ['process_image.py', args.image]
        image_main()
        return
    
    # If no arguments, show help
    parser.print_help()

if __name__ == "__main__":
    main()
