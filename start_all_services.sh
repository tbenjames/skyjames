#!/bin/bash
# SkyJames - Start All Services

echo "🚀 Starting All SkyJames Services"
echo "=================================="

# 1. Start Mobile API
echo "📱 Starting Mobile API on port 5002..."
python src/mobile_api.py &
sleep 2

# 2. Start WebSocket Server
echo "🔌 Starting WebSocket Server on port 8767..."
python src/websocket_server.py &
sleep 2

# 3. Start Advanced Features
echo "⚙️ Starting Advanced Features..."
python -c "from src.advanced_features import video_stream_processor, analytics; print('✅ Advanced features loaded')" &

# 4. Start Production Monitor
echo "📊 Starting Production Monitor..."
python -c "from src.production_monitor import monitor; print('✅ Production monitor active')" &

# 5. Start Cloud Deployer
echo "☁️ Cloud deployer ready. Run: ./deploy_cloud.sh"

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Services:"
echo "  - Mobile API: http://localhost:5002"
echo "  - WebSocket: ws://localhost:8767"
echo "  - Main API: http://localhost:5001"
echo "  - MLflow: http://localhost:5000"
echo "  - Dashboard: http://localhost:8501"
echo "  - Analytics: http://localhost:8503"
echo ""
echo "📱 To build mobile app, use mobile_app_example.js"
echo "☁️ To deploy to cloud, run: ./deploy_cloud.sh"
echo "=================================="
