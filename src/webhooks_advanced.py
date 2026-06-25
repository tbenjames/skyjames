"""
SkyJames - Advanced Webhook Integration
"""

import json
import requests
import threading
import queue
import time
from datetime import datetime
from urllib.parse import urlparse

class WebhookManager:
    def __init__(self):
        self.webhooks = {}
        self.event_queue = queue.Queue()
        self.worker = threading.Thread(target=self._process_events, daemon=True)
        self.worker.start()
        self.event_history = []
        self.retry_config = {
            'max_retries': 3,
            'backoff_factor': 2,
            'timeout': 10
        }
    
    def register(self, event_type, url, headers=None, retry_config=None):
        """Register a webhook"""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        
        self.webhooks[event_type].append({
            'url': url,
            'headers': headers or {},
            'retry_config': retry_config or self.retry_config,
            'active': True,
            'created': datetime.now().isoformat()
        })
        return True
    
    def trigger(self, event_type, data):
        """Trigger a webhook event"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.event_queue.put(event)
    
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
        """Send webhook with retry logic"""
        config = webhook.get('retry_config', self.retry_config)
        url = webhook['url']
        
        for attempt in range(config['max_retries']):
            try:
                response = requests.post(
                    url,
                    json=event,
                    headers=webhook['headers'],
                    timeout=config['timeout']
                )
                if response.status_code < 400:
                    self._log_event(url, event, 'success')
                    return True
                time.sleep(config['backoff_factor'] ** attempt)
            except:
                time.sleep(config['backoff_factor'] ** attempt)
        
        self._log_event(url, event, 'failed')
        return False
    
    def _log_event(self, url, event, status):
        """Log webhook event"""
        self.event_history.append({
            'url': url,
            'event': event,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
    
    def get_stats(self):
        """Get webhook statistics"""
        return {
            'total_webhooks': len(self.webhooks),
            'recent_events': len(self.event_history),
            'webhooks': list(self.webhooks.keys())
        }

# Global webhook manager
webhook_manager = WebhookManager()
