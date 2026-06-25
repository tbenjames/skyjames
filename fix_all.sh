#!/bin/bash
# SkyJames Quick Fix Script

echo "🔧 Fixing SkyJames Services..."

# 1. Kill everything
echo "1️⃣ Killing old services..."
pkill -f "mlflow" 2>/dev/null
pkill -f "streamlit" 2>/dev/null
pkill -f "webrtc_stream" 2>/dev/null
pkill -f "scheduler" 2>/dev/null
pkill -f "api_server" 2>/dev/null
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
lsof -ti:8502 | xargs kill -9 2>/dev/null
lsof -ti:8503 | xargs kill -9 2>/dev/null
lsof -ti:8765 | xargs kill -9 2>/dev/null
lsof -ti:8766 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null
sleep 2

# 2. Check module imports
echo "2️⃣ Testing imports..."
python -c "from src.perception.lane_net_cpu import OptimizedLaneDetector; print('✅ Lane detector imported')"
python -c "from src.config import Config; print('✅ Config imported')"

# 3. Launch fixed services
echo "3️⃣ Launching services..."
python launch_advanced_fixed.py &
sleep 5

# 4. Test connection
echo "4️⃣ Testing connections..."
curl -s http://localhost:5001/status || echo "⚠️ API not ready yet"
python test_webrtc.py

echo ""
echo "✅ Fix complete!"
echo ""
echo "📊 Access your services:"
echo "  - MLflow: http://localhost:5000"
echo "  - Dashboard: http://localhost:8501"
echo "  - Analytics: http://localhost:8503"
echo "  - API: http://localhost:5001"
echo ""
