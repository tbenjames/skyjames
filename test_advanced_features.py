"""
SkyJames - Test All Advanced Features
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Testing SkyJames Advanced Features")
print("=" * 50)

# 1. Test Video Summarization
print("\n1️⃣ Testing Video Summarization...")
try:
    from src.video_summarization import VideoSummarizer
    summarizer = VideoSummarizer()
    print("   ✅ Video Summarization ready")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Test Text Search
print("\n2️⃣ Testing Text Search...")
try:
    from src.text_search import VideoSearch
    search = VideoSearch()
    search.index_video("test.mp4", "Test video")
    results = search.search("test")
    print(f"   ✅ Text Search ready (found {len(results)} results)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Test Collaboration
print("\n3️⃣ Testing Collaboration...")
try:
    from src.collaboration import CollaborationManager
    collab = CollaborationManager()
    collab.create_room("test_room")
    collab.join_room("test_room", "User1")
    collab.send_message("test_room", "User1", "Hello")
    print("   ✅ Collaboration ready")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Advanced features test complete!")
