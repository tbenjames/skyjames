#!/bin/bash
echo "📦 Setting up MQTT broker..."

# Install MQTT via Docker
docker run -d \
  --name skyjames-mqtt \
  -p 1883:1883 \
  -p 9001:9001 \
  eclipse-mosquitto

echo "✅ MQTT broker started on port 1883"
