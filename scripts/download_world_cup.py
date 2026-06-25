"""
Download World Cup videos for analysis
"""

import os
import subprocess
import sys

def download_world_cup_video():
    """Download a World Cup highlight video"""
    
    print("=" * 60)
    print("🏆 WORLD CUP VIDEO DOWNLOADER")
    print("=" * 60)
    
    # World Cup highlight videos (replace with working URLs)
    videos = [
        {
            'name': 'world_cup_highlights_2022',
            'url': 'https://www.youtube.com/watch?v=NR7t7G_3q30'  # Replace with actual
        },
        {
            'name': 'world_cup_goals',
            'url': 'https://www.youtube.com/watch?v=8sX7pUnEGww'  # Replace with actual
        }
    ]
    
    os.makedirs("data/sports", exist_ok=True)
    
    print("\n🎯 Downloading World Cup videos...")
    print("   (You can replace the URLs with actual World Cup video links)")
    
    try:
        # Check if yt-dlp is installed
        subprocess.run(["yt-dlp", "--version"], capture_output=True)
        has_ytdlp = True
    except:
        has_ytdlp = False
        print("\n⚠ yt-dlp not installed. Install with: pip install yt-dlp")
    
    if has_ytdlp:
        for video in videos:
            try:
                print(f"\nDownloading: {video['name']}")
                subprocess.run([
                    "yt-dlp",
                    "-f", "best[ext=mp4]",
                    "-o", f"data/sports/{video['name']}.%(ext)s",
                    "--no-playlist",
                    video['url']
                ], check=True)
                print(f"✅ Downloaded: {video['name']}")
            except Exception as e:
                print(f"❌ Failed to download {video['name']}: {e}")
    else:
        print("\n📝 To download World Cup videos manually:")
        print("1. Find a World Cup video on YouTube")
        print("2. Copy the URL")
        print("3. Replace the URL in this script")
        print("4. Run: pip install yt-dlp")
        print("5. Run this script again")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    download_world_cup_video()
