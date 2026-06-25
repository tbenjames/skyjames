#!/usr/bin/env python
"""
SkyJames - Production Computer Vision Pipeline
Main entry point for the application
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.perception.object_detector import ObjectDetector
from src.safety.safety_monitor import SafetyMonitor

def print_banner():
    """Print SkyJames banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ███████╗██╗  ██╗██╗   ██╗██╗ █████╗  ██████╗███████╗    ║
    ║   ██╔════╝██║ ██╔╝╚██╗ ██╔╝██║██╔══██╗██╔════╝██╔════╝    ║
    ║   ███████╗█████╔╝  ╚████╔╝ ██║███████║██║     █████╗      ║
    ║   ╚════██║██╔═██╗   ╚██╔╝  ██║██╔══██║██║     ██╔══╝      ║
    ║   ███████║██║  ██╗   ██║   ██║██║  ██║╚██████╗███████╗    ║
    ║   ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝    ║
    ║                                                              ║
    ║   Production Computer Vision Pipeline for Autonomous Systems ║
    ║   Version 2.0.0                                              ║
    ║   © 2024 SkyJames AI                                         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    parser = argparse.ArgumentParser(description='SkyJames - Production Computer Vision Pipeline')
    parser.add_argument('--mode', type=str, choices=['webcam', 'video', 'sports', 'dashboard', 'api', 'stream'],
                       default='webcam', help='Run mode')
    parser.add_argument('--video', type=str, help='Path to input video')
    parser.add_argument('--output', type=str, help='Path to output video')
    parser.add_argument('--no-neural', action='store_true', help='Disable neural network')
    
    args = parser.parse_args()
    
    print_banner()
    print(f"🚀 SkyJames v{Config.PROJECT_VERSION} initialized")
    print(f"📁 Working directory: {Config.BASE_DIR}")
    
    if args.mode == 'webcam':
        print("\n📹 Starting webcam mode...")
        from scripts.webcam_pipeline import main as webcam_main
        webcam_main()
    
    elif args.mode == 'video':
        print(f"\n🎬 Processing video: {args.video}")
        from scripts.run_pipeline_with_model import main as pipeline_main
        # Pass arguments to pipeline
        sys.argv = ['run_pipeline_with_model.py']
        if args.video:
            sys.argv.extend(['--video', args.video])
        if args.output:
            sys.argv.extend(['--output', args.output])
        if args.no_neural:
            sys.argv.append('--no-neural')
        pipeline_main()
    
    elif args.mode == 'sports':
        print("\n⚽ Starting sports analysis...")
        from scripts.football_analysis import main as sports_main
        sports_main()
    
    elif args.mode == 'dashboard':
        print("\n📊 Starting dashboard...")
        import subprocess
        subprocess.run(['streamlit', 'run', 'scripts/dashboard_app.py'])
    
    elif args.mode == 'api':
        print("\n🌐 Starting API server...")
        from scripts.api_server import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    
    elif args.mode == 'stream':
        print("\n📡 Starting WebRTC stream...")
        import asyncio
        from scripts.webrtc_stream import WebRTCStreamer
        streamer = WebRTCStreamer()
        asyncio.run(streamer.start())

if __name__ == "__main__":
    main()
