"""
Download World Cup 2026 videos with guidance
"""

import os
import subprocess
import sys

def download_video():
    """Interactive video downloader for World Cup"""
    
    print("=" * 60)
    print("🏆 WORLD CUP 2026 VIDEO DOWNLOADER")
    print("=" * 60)
    
    print("\n📝 HOW TO DOWNLOAD WORLD CUP VIDEOS:")
    print("1. Go to YouTube and search for 'World Cup 2026 highlights'")
    print("2. Copy the video URL (e.g., https://www.youtube.com/watch?v=XXXXX)")
    print("3. Enter the URL below")
    print("\nOR use these sources:")
    print("   • FIFA+: https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026")
    print("   • FOX Sports: https://www.foxsports.com/soccer/world-cup")
    print("   • YouTube: Search 'World Cup 2026 highlights'")
    
    print("\n" + "=" * 60)
    
    # Check if yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        has_ytdlp = True
        print("✅ yt-dlp is installed")
    except:
        has_ytdlp = False
        print("❌ yt-dlp is NOT installed")
        print("   Install with: pip install yt-dlp")
    
    if has_ytdlp:
        print("\n📥 Enter the video URL (or press Enter to skip):")
        url = input("URL: ").strip()
        
        if url and url.startswith("http"):
            print(f"\nDownloading: {url}")
            try:
                # Create directory
                os.makedirs("data/worldcup", exist_ok=True)
                
                # Download
                subprocess.run([
                    "yt-dlp",
                    "-f", "best[ext=mp4]",
                    "-o", "data/worldcup/worldcup_%(title)s.%(ext)s",
                    "--no-playlist",
                    url
                ], check=True)
                
                print("\n✅ Download complete! Check data/worldcup/")
                
                # List downloaded files
                print("\n📁 Files in data/worldcup/:")
                for f in os.listdir("data/worldcup"):
                    if f.endswith(('.mp4', '.avi', '.mov')):
                        size = os.path.getsize(f"data/worldcup/{f}") / (1024 * 1024)
                        print(f"   • {f} ({size:.1f} MB)")
                        
            except Exception as e:
                print(f"❌ Download failed: {e}")
                print("\nPlease try a different URL or download manually.")
        else:
            print("⏭️ Skipping download.")
    
    print("\n" + "=" * 60)
    print("📂 Manual Download Instructions:")
    print("1. Download a World Cup video manually")
    print("2. Save it to: data/worldcup/match.mp4")
    print("3. Run: python scripts/worldcup_analysis.py data/worldcup/match.mp4")
    print("=" * 60)

if __name__ == "__main__":
    download_video()
