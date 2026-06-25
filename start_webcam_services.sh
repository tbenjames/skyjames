#!/bin/bash
echo "📹 Starting SkyJames Webcam Services"
echo "====================================="

# Start Webcam API
echo "📡 Starting Webcam API on port 5003..."
python scripts/webcam_api.py &
WEBCAM_API_PID=$!
sleep 2

# Start Webcam Dashboard
echo "📊 Starting Webcam Dashboard on port 8504..."
streamlit run scripts/webcam_dashboard.py --server.port 8504 --server.headless true &
WEBCAM_DASHBOARD_PID=$!

echo ""
echo "✅ All Webcam Services Started!"
echo ""
echo "📊 Access URLs:"
echo "  - Webcam Dashboard: http://localhost:8504"
echo "  - Webcam API: http://localhost:5003"
echo ""
echo "📱 Mobile Access:"
echo "  http://YOUR_IP:8504"
echo ""
echo "Press Ctrl+C to stop all services"
wait
