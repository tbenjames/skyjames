#!/bin/bash
# SkyJames Quick Test Script

echo "🚀 SkyJames Quick Test"
echo "======================"

# Check Python environment
echo "📌 Python version: $(python3 --version)"

# Check directories
echo "📌 Checking directories..."
for dir in data/input data/output data/sports models tests; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir (creating...)"
        mkdir -p "$dir"
    fi
done

# Check test video
echo "📌 Checking test video..."
if [ -f "data/input/test_video.avi" ]; then
    echo "  ✅ Test video exists"
else
    echo "  ⚠️ Test video not found (creating...)"
    python3 scripts/generate_test_video.py
fi

# Check model
echo "📌 Checking model..."
if [ -f "models/lane_net_optimized.pth" ]; then
    echo "  ✅ Model exists"
else
    echo "  ⚠️ Model not found (using fallback)"
fi

# Test imports
echo "📌 Testing imports..."
python3 -c "
import cv2, numpy, torch, streamlit, plotly, matplotlib
print('  ✅ All imports successful')
" 2>/dev/null || echo "  ❌ Some imports failed"

# Run quick test
echo ""
echo "🧪 Running quick test..."
python3 tests/test_suite.py quick

echo ""
echo "✅ Quick test complete!"
echo ""
echo "To run full tests: python3 tests/test_suite.py all"
echo "To test API: python3 tests/test_suite.py api"
