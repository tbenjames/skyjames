"""
SkyJames - Webhook Integration
"""

import requests
import json
import threading
import queue
from datetime import datetime

class WebhookManager:
    def __init__(self):
        self.webhooks = {}
        self.event_queue = queue.Queue()
        self.worker = threading.Thread(target=self._process_events, daemon=True)
        self.worker.start()
    
    def register_webhook(self, event_type, url, headers=None):
        """Register a webhook for an event"""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        self.webhooks[event_type].append({
            'url': url,
            'headers': headers or {},
            'active': True
        })
        return True
    
    def trigger_event(self, event_type, data):
        """Trigger a webhook event"""
        self.event_queue.put({
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def _process_events(self):
        """Process webhook events"""
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                if event['type'] in self.webhooks:
                    for webhook in self.webhooks[event['type']]:
                        if webhook['active']:
                            self._send_webhook(webhook, event)
            except queue.Empty:
                continue
    
    def _send_webhook(self, webhook, event):
        """Send webhook request"""
        try:
            response = requests.post(
                webhook['url'],
                json=event,
                headers=webhook['headers'],
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

# Events
EVENT_VIDEO_PROCESSED = 'video_processed'
EVENT_DETECTION_MADE = 'detection_made'
EVENT_ALERT_TRIGGERED = 'alert_triggered'
EVENT_MODEL_UPDATED = 'model_updated'

# Example usage
def setup_webhooks():
    webhook_manager = WebhookManager()
    
    # Register webhooks
    webhook_manager.register_webhook(
        EVENT_VIDEO_PROCESSED,
        'https://api.yourservice.com/video_complete',
        {'Authorization': 'Bearer YOUR_TOKEN'}
    )
    
    webhook_manager.register_webhook(
        EVENT_ALERT_TRIGGERED,
        'https://api.yourservice.com/alert',
        {'Authorization': 'Bearer YOUR_TOKEN'}
    )
    
    return webhook_manager
