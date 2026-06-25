#!/bin/bash
# SkyJames Model Launcher

echo "🚀 SkyJames Model System"
echo "========================="

# Install dependencies
echo "📦 Installing model dependencies..."
pip install ultralytics boxmot

# Download YOLO11 models
echo "📥 Downloading YOLO11 models..."
python -c "
from ultralytics import YOLO
models = [
    'yolo11n.pt',
    'yolo11n-seg.pt', 
    'yolo11n-pose.pt',
    'yolo11n-obb.pt'
]
for m in models:
    try:
        print(f'Downloading {m}...')
        YOLO(m)
        print(f'✅ {m} downloaded')
    except:
        print(f'⚠️ Failed to download {m}')
"

# Run model test
echo ""
echo "🧪 Testing models..."
python scripts/test_models.py

echo ""
echo "✅ Model setup complete!"
echo ""
echo "📊 Available models:"
echo "  - YOLO11 (detection)"
echo "  - YOLO11-seg (segmentation)"
echo "  - YOLO11-pose (pose estimation)"
echo "  - YOLO11-obb (oriented bbox)"
echo "  - ByteTrack (tracking)"
echo ""
echo "🚀 To use models in dashboard:"
echo "  streamlit run scripts/model_dashboard.py"
