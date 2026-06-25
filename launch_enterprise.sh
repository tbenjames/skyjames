#!/bin/bash
# SkyJames Enterprise Launcher

echo "🚀 SkyJames Enterprise Edition"
echo "==============================="

# Kill existing processes
pkill -f "streamlit" 2>/dev/null
pkill -f "mlflow" 2>/dev/null
sleep 2

# Set Python path
export PYTHONPATH=/Users/apple/lane-detection:$PYTHONPATH

# Start MLflow
echo "📊 Starting MLflow..."
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts --host 0.0.0.0 --port 5000 &
sleep 3

# Start Main Dashboard
echo "📈 Starting Main Dashboard on port 8501..."
streamlit run scripts/dashboard_app.py --server.port 8501 --server.headless true &
sleep 2

# Start Report Dashboard
echo "📊 Starting Report Dashboard on port 8502..."
streamlit run scripts/report_dashboard.py --server.port 8502 --server.headless true &
sleep 2

# Start 3D Visualization
echo "🌐 Starting 3D Visualization on port 8503..."
streamlit run scripts/3d_visualization.py --server.port 8503 --server.headless true &

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Access URLs:"
echo "  - MLflow: http://localhost:5000"
echo "  - Main Dashboard: http://localhost:8501 (Webcam + Models)"
echo "  - Report Dashboard: http://localhost:8502"
echo "  - 3D Visualization: http://localhost:8503"
echo ""
echo "📱 On mobile, use your IP:"
echo "  - http://YOUR_IP:8501"
echo ""
echo "Press Ctrl+C to stop all services"
wait
