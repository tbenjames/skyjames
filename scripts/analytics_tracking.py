"""
SkyJames - Usage Analytics
"""

import json
import os
from datetime import datetime

class Analytics:
    def __init__(self):
        self.analytics_file = "data/analytics.json"
        self.load()
    
    def load(self):
        try:
            with open(self.analytics_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {
                'users': 0,
                'videos_processed': 0,
                'detections': 0,
                'start_time': datetime.now().isoformat()
            }
    
    def save(self):
        os.makedirs('data', exist_ok=True)
        with open(self.analytics_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def track_user(self):
        self.data['users'] += 1
        self.save()
    
    def track_video(self):
        self.data['videos_processed'] += 1
        self.save()
    
    def track_detection(self):
        self.data['detections'] += 1
        self.save()
    
    def get_stats(self):
        return self.data

# Usage
analytics = Analytics()
print(f"📊 SkyJames Analytics:")
print(f"  Users: {analytics.data['users']}")
print(f"  Videos: {analytics.data['videos_processed']}")
print(f"  Detections: {analytics.data['detections']}")
