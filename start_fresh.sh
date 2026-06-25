#!/bin/bash
# SkyJames - Fresh Start All Services

echo "🚀 SkyJames - Fresh Start"
echo "=========================="

# 1. MLflow
echo "📊 Starting MLflow..."
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts --host 0.0.0.0 --port 5000 &
MLFLOW_PID=$!
sleep 3

# 2. Main API
echo "🌐 Starting Main API..."
python scripts/api_server.py &
API_PID=$!
sleep 2

# 3. Main Dashboard
echo "📈 Starting Main Dashboard..."
streamlit run scripts/dashboard_app.py --server.port 8501 &
DASHBOARD_PID=$!
sleep 2

# 4. Model Dashboard
echo "🤖 Starting Model Dashboard..."
streamlit run scripts/model_dashboard_final.py --server.port 8505 &
MODEL_PID=$!
sleep 2

# 5. Mobile API (optional)
echo "📱 Starting Mobile API..."
python src/mobile_api.py &
MOBILE_PID=$!
sleep 2

# 6. WebSocket (optional)
echo "🔌 Starting WebSocket..."
python src/websocket_server.py &
WEBSOCKET_PID=$!
sleep 2

# 7. Webcam Server (optional)
echo "📹 Starting Webcam Server..."
python webcam_simple.py &
WEBCAM_PID=$!

echo ""
echo "✅ All Services Started!"
echo ""
echo "📊 Services:"
echo "  - MLflow: http://localhost:5000"
echo "  - Main API: http://localhost:5001"
echo "  - Mobile API: http://localhost:5002"
echo "  - Webcam API: http://localhost:5004"
echo "  - WebSocket: ws://localhost:8767"
echo "  - Main Dashboard: http://localhost:8501"
echo "  - Model Dashboard: http://localhost:8505"
echo ""
echo "📱 Mobile Access:"
echo "  - http://YOUR_IP:8501 (Dashboard)"
echo "  - http://YOUR_IP:8505 (Models)"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================="

wait
