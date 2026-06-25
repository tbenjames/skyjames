"""
SkyJames - WebSocket Server for Real-time Updates
"""

import asyncio
import websockets
import json
import threading
from datetime import datetime

class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=8767):
        self.host = host
        self.port = port
        self.clients = set()
        self.latest_data = {}
    
    async def handler(self, websocket):
        """Handle WebSocket connection"""
        print(f"🔌 Client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                data = json.loads(message)
                if data.get('type') == 'subscribe':
                    self.latest_data['subscription'] = data.get('topic', 'all')
                    response = {'type': 'subscribed', 'topic': data.get('topic', 'all')}
                    await websocket.send(json.dumps(response))
                
                elif data.get('type') == 'ping':
                    await websocket.send(json.dumps({'type': 'pong', 'timestamp': datetime.now().isoformat()}))
                
                elif data.get('type') == 'data':
                    self.latest_data['data'] = data.get('payload', {})
                    # Broadcast to all clients
                    await self.broadcast(json.dumps({
                        'type': 'update',
                        'data': self.latest_data['data'],
                        'timestamp': datetime.now().isoformat()
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Client disconnected: {websocket.remote_address}")
        finally:
            self.clients.discard(websocket)
    
    async def broadcast(self, message):
        """Broadcast message to all clients"""
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])
    
    async def start(self):
        """Start WebSocket server"""
        print(f"🔌 WebSocket server starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()

# Start server
def start_websocket_server():
    server = WebSocketServer()
    asyncio.run(server.start())

if __name__ == "__main__":
    start_websocket_server()
