"""
Test WebRTC Connection
"""

import asyncio
import websockets
import json

async def test_connection():
    try:
        uri = "ws://localhost:8766"
        async with websockets.connect(uri) as websocket:
            # Send status request
            await websocket.send(json.dumps({"type": "status"}))
            response = await websocket.recv()
            print(f"✅ WebRTC response: {response}")
            return True
    except Exception as e:
        print(f"❌ WebRTC connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
