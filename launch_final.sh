#!/bin/bash
echo "🚀 SkyJames Final Launch"
echo "========================"

# Kill existing
pkill -f "streamlit" 2>/dev/null
sleep 2

export PYTHONPATH=/Users/apple/lane-detection:$PYTHONPATH

echo "📈 Starting dashboard..."
streamlit run scripts/dashboard_clean.py --server.port 8501 --server.address 0.0.0.0

echo ""
echo "✅ Dashboard running at: http://localhost:8501"
