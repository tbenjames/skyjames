"""
Download sample driving videos from open sources
"""

import os
import urllib.request
import sys

def download_file(url, filename):
    """Download a file with progress"""
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"✓ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def main():
    print("=" * 60)
    print("DOWNLOADING SAMPLE VIDEOS")
    print("=" * 60)
    
    os.makedirs("data/real_videos", exist_ok=True)
    
    # Sample videos from various sources
    videos = [
        {
            'name': 'highway_drive.mp4',
            'url': 'https://www.dropbox.com/s/example1.mp4?dl=1'  # Replace with actual URL
        },
        {
            'name': 'city_drive.mp4', 
            'url': 'https://www.dropbox.com/s/example2.mp4?dl=1'  # Replace with actual URL
        }
    ]
    
    print("\nSince direct download links may not work, please:")
    print("1. Download videos manually from:")
    print("   - https://www.kaggle.com/datasets/")
    print("   - https://open-datasets.com/")
    print("   - https://www.youtube.com (then convert to MP4)")
    print("\n2. Or use your own driving videos")
    print("\n3. Or use the synthetic test video we already have")
    
    # Check if we have the synthetic video
    if os.path.exists("data/input/synthetic_road.mp4"):
        print("\n✓ Using synthetic video for testing: data/input/synthetic_road.mp4")
        
        # Copy to real_videos for testing
        import shutil
        shutil.copy("data/input/synthetic_road.mp4", "data/real_videos/synthetic_drive.mp4")
        print("  Copied to: data/real_videos/synthetic_drive.mp4")

if __name__ == "__main__":
    main()
