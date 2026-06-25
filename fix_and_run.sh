#!/bin/bash
# One-click fix and run

echo "🔧 Fixing SkyJames..."
echo "==============================="

# Kill everything
pkill -f "streamlit" 2>/dev/null
pkill -f "mlflow" 2>/dev/null
sleep 2

# Set Python path
export PYTHONPATH=/Users/apple/lane-detection:$PYTHONPATH

# Test import
echo "Testing imports..."
python -c "
import sys
sys.path.insert(0, '/Users/apple/lane-detection')
from src.model_manager_no_track import load_all_models
print('✅ Import successful!')
" || echo "❌ Import failed, please check src directory"

# Start services
echo "Starting services..."
./launch_with_path.sh
