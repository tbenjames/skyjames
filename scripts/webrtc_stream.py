"""
SkyJames - WebRTC Real-time Streaming
"""

import cv2
import json
import asyncio
import websockets
import base64
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

class SkyJamesStreamer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.detector = OptimizedLaneDetector(Config())
        self.clients = set()
        self.stream_name = "SkyJames Live Stream"
    
    async def handle_client(self, websocket, path):
        """Handle client connection"""
        print(f"📱 SkyJames client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'frame':
                    img_data = base64.b64decode(data['data'])
                    nparr = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    # Process frame
                    result, left, right = self.detector.process_frame(frame)
                    
                    # Add SkyJames branding
                    cv2.putText(result, "SkyJames AI", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # Encode result
                    _, buffer = cv2.imencode('.jpg', result)
                    result_data = base64.b64encode(buffer).decode('utf-8')
                    
                    response = {
                        'type': 'processed',
                        'data': result_data,
                        'lanes': {'left': left, 'right': right},
                        'stream': self.stream_name
                    }
                    await websocket.send(json.dumps(response))
                
                elif data['type'] == 'status':
                    response = {
                        'type': 'status',
                        'status': 'ready',
                        'model': 'lane_net_optimized.pth',
                        'fps': 30,
                        'stream': self.stream_name
                    }
                    await websocket.send(json.dumps(response))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"📱 SkyJames client disconnected: {websocket.remote_address}")
        finally:
            self.clients.remove(websocket)
    
    async def start(self):
        """Start WebRTC server"""
        print(f"🌐 SkyJames WebRTC server starting on ws://{self.host}:{self.port}")
        print(f"📡 Stream: {self.stream_name}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()

if __name__ == "__main__":
    streamer = SkyJamesStreamer()
    asyncio.run(streamer.start())
