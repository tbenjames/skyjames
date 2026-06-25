#!/bin/bash
echo "🚀 SkyJames Clean Edition"
echo "========================="

# Kill existing
pkill -f "streamlit" 2>/dev/null
sleep 2

export PYTHONPATH=/Users/apple/lane-detection:$PYTHONPATH

echo "📈 Starting Clean Dashboard..."
streamlit run scripts/dashboard_clean.py --server.port 8501 --server.headless true &

echo ""
echo "✅ Dashboard started!"
echo ""
echo "📊 Access: http://localhost:8501"
echo "📱 Mobile: http://YOUR_IP:8501"
echo ""
echo "Press Ctrl+C to stop"
wait
