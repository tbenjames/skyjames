#!/bin/bash
# SkyJames Edge Deployment Script

echo "🚀 SkyJames Edge Deployment"
echo "============================"

# Install dependencies for edge
pip install --upgrade pip
pip install onnx onnxruntime

# Convert model to ONNX for edge deployment
python3 -c "
import torch
from src.perception.lane_net_cpu import LaneNetCPU
model = LaneNetCPU()
model.load_state_dict(torch.load('models/lane_net_optimized.pth', map_location='cpu'))
model.eval()
dummy_input = torch.randn(1, 3, 128, 256)
torch.onnx.export(model, dummy_input, 'models/lane_net_optimized.onnx')
print('✅ Model converted to ONNX for edge deployment')
"

# Optimize for Raspberry Pi
echo "📦 Creating Raspberry Pi deployment package..."
mkdir -p deploy/raspberry_pi
cp -r src deploy/raspberry_pi/
cp requirements.txt deploy/raspberry_pi/
cp models/lane_net_optimized.onnx deploy/raspberry_pi/
cat > deploy/raspberry_pi/run.sh << 'SCRIPT'
#!/bin/bash
# Run on Raspberry Pi
echo "🚀 Running SkyJames on Raspberry Pi..."
python3 src/pipeline.py
SCRIPT

chmod +x deploy/raspberry_pi/run.sh

echo "✅ Edge deployment package created in deploy/"
