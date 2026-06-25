
"""
SkyJames - Webhook Integration
"""

import requests
import threading
import queue
from datetime import datetime

class WebhookManager:
    def __init__(self):
        self.webhooks = {}
        self.event_queue = queue.Queue()
        self.worker = threading.Thread(target=self._process_events, daemon=True)
        self.worker.start()
        print("✅ Webhook manager initialized")
    
    def register_webhook(self, event_type, url, headers=None):
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        self.webhooks[event_type].append({
            "url": url,
            "headers": headers or {},
            "active": True
        })
        return True
    
    def trigger_event(self, event_type, data):
        self.event_queue.put({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def _process_events(self):
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                if event["type"] in self.webhooks:
                    for webhook in self.webhooks[event["type"]]:
                        if webhook["active"]:
                            self._send_webhook(webhook, event)
            except queue.Empty:
                continue
    
    def _send_webhook(self, webhook, event):
        try:
            response = requests.post(
                webhook["url"],
                json=event,
                headers=webhook["headers"],
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

EVENT_VIDEO_PROCESSED = "video_processed"
EVENT_DETECTION_MADE = "detection_made"
EVENT_ALERT_TRIGGERED = "alert_triggered"

def setup_webhooks():
    webhook_manager = WebhookManager()
    return webhook_manager
