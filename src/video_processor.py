"""
SkyJames - Advanced Video Processing
"""

import subprocess
import os
import cv2
import numpy as np
from pathlib import Path

class VideoProcessor:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"  # Ensure ffmpeg is installed
    
    def extract_keyframes(self, video_path, output_dir="frames"):
        """Extract keyframes from video using ffmpeg"""
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", "select='eq(pict_type,I)'",
            "-vsync", "0",
            f"{output_dir}/keyframe_%04d.jpg"
        ]
        
        subprocess.run(cmd, check=True)
        return len(os.listdir(output_dir))
    
    def extract_audio(self, video_path, output_path="audio.wav"):
        """Extract audio from video"""
        cmd = ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", output_path]
        subprocess.run(cmd, check=True)
        return output_path
    
    def generate_thumbnail(self, video_path, timestamp=1.0):
        """Generate thumbnail at specific timestamp"""
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-vf", "scale=320:180",
            "thumbnail.jpg"
        ]
        subprocess.run(cmd, check=True)
        return "thumbnail.jpg"
    
    def resize_video(self, video_path, output_path, width=640, height=480):
        """Resize video"""
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"scale={width}:{height}",
            "-c:a", "copy",
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path
    
    def add_overlay(self, video_path, overlay_text, output_path=None):
        """Add text overlay to video"""
        if output_path is None:
            output_path = f"overlay_{os.path.basename(video_path)}"
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:x=10:y=10",
            "-c:a", "copy",
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path
    
    def create_concatenated_video(self, video_paths, output_path):
        """Concatenate multiple videos"""
        concat_file = "concat_list.txt"
        with open(concat_file, "w") as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")
        
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", output_path]
        subprocess.run(cmd, check=True)
        os.remove(concat_file)
        return output_path
