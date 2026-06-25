"""
SkyJames - IoT Sensor Integration
Supports: MQTT, WebSocket, HTTP endpoints
"""

import json
import threading
import time
import requests
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except:
    MQTT_AVAILABLE = False
    print("⚠️ MQTT not installed - install with: pip install paho-mqtt")

class IoTManager:
    def __init__(self):
        self.sensors = {}
        self.sensor_data = {}
        self.mqtt_client = None
        self.websocket_connections = {}
        self.running = False
        self.thread = None
    
    def add_sensor(self, sensor_id, sensor_type, config):
        """Register a new sensor"""
        self.sensors[sensor_id] = {
            'type': sensor_type,
            'config': config,
            'added': datetime.now().isoformat(),
            'active': True
        }
        self.sensor_data[sensor_id] = []
        return sensor_id
    
    def get_sensor_data(self, sensor_id, limit=100):
        """Get sensor data"""
        if sensor_id in self.sensor_data:
            return self.sensor_data[sensor_id][-limit:]
        return []
    
    def update_sensor_data(self, sensor_id, data):
        """Update sensor data"""
        if sensor_id in self.sensor_data:
            self.sensor_data[sensor_id].append({
                'timestamp': datetime.now().isoformat(),
                'data': data
            })
            # Keep only last 1000 entries
            if len(self.sensor_data[sensor_id]) > 1000:
                self.sensor_data[sensor_id] = self.sensor_data[sensor_id][-1000:]
    
    def connect_mqtt(self, broker="localhost", port=1883):
        """Connect to MQTT broker"""
        if not MQTT_AVAILABLE:
            return False
        
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start()
            return True
        except:
            return False
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Handle MQTT message"""
        try:
            data = json.loads(msg.payload.decode())
            # Auto-register sensor if not exists
            sensor_id = f"mqtt_{msg.topic}"
            if sensor_id not in self.sensors:
                self.add_sensor(sensor_id, 'mqtt', {'topic': msg.topic})
            self.update_sensor_data(sensor_id, data)
        except:
            pass
    
    def subscribe_mqtt(self, topic):
        """Subscribe to MQTT topic"""
        if self.mqtt_client:
            self.mqtt_client.subscribe(topic)
            return True
        return False
    
    def send_webhook(self, url, data, headers=None):
        """Send data to webhook"""
        try:
            response = requests.post(
                url,
                json=data,
                headers=headers or {},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def start(self):
        """Start IoT manager"""
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
    
    def _process_loop(self):
        """Background processing loop"""
        while self.running:
            # Process sensor data
            time.sleep(1)

# Global IoT manager
iot_manager = IoTManager()
