"""
SkyJames - Real-time Notifications
"""

import asyncio
import json
from datetime import datetime

class NotificationManager:
    def __init__(self):
        self.subscribers = {}
        self.notifications = []
    
    def subscribe(self, client_id, callback):
        self.subscribers[client_id] = callback
        return True
    
    def unsubscribe(self, client_id):
        if client_id in self.subscribers:
            del self.subscribers[client_id]
            return True
        return False
    
    def send_notification(self, message, type="info"):
        notification = {
            'id': len(self.notifications) + 1,
            'type': type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        
        # Send to all subscribers
        for client_id, callback in self.subscribers.items():
            try:
                callback(notification)
            except:
                pass
        
        return notification
    
    def get_notifications(self, limit=50):
        return self.notifications[-limit:]

# WebSocket support
async def websocket_handler(websocket, path):
    manager = NotificationManager()
    client_id = id(websocket)
    
    def callback(notification):
        asyncio.create_task(websocket.send(json.dumps(notification)))
    
    manager.subscribe(client_id, callback)
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get('type') == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))
    finally:
        manager.unsubscribe(client_id)
