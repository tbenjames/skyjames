"""
SkyJames - WebRTC Real-time Streaming (Fixed)
"""

import cv2
import json
import asyncio
import websockets
import base64
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

class SkyJamesStreamer:
    def __init__(self, host='0.0.0.0', port=8766):
        self.host = host
        self.port = port
        self.detector = OptimizedLaneDetector(Config())
        self.clients = set()
    
    async def handler(self, websocket):
        """Handle client connection"""
        print(f"📱 Client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('type') == 'frame':
                        # Decode frame
                        img_data = base64.b64decode(data['data'])
                        nparr = np.frombuffer(img_data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            # Process frame
                            result, left, right = self.detector.process_frame(frame)
                            
                            # Encode result
                            _, buffer = cv2.imencode('.jpg', result)
                            result_data = base64.b64encode(buffer).decode('utf-8')
                            
                            response = {
                                'type': 'processed',
                                'data': result_data,
                                'lanes': {'left': left, 'right': right}
                            }
                            await websocket.send(json.dumps(response))
                    
                    elif data.get('type') == 'status':
                        response = {
                            'type': 'status',
                            'status': 'ready',
                            'fps': 30,
                            'model': 'lane_net_optimized.pth'
                        }
                        await websocket.send(json.dumps(response))
                
                except json.JSONDecodeError:
                    print("⚠️ Invalid JSON received")
                except Exception as e:
                    print(f"⚠️ Error processing message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"📱 Client disconnected: {websocket.remote_address}")
        finally:
            self.clients.discard(websocket)
    
    async def start(self):
        print(f"🌐 WebRTC server starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()

if __name__ == "__main__":
    streamer = SkyJamesStreamer()
    asyncio.run(streamer.start())
