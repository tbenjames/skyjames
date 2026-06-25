#!/bin/bash
# SkyJames Production Deployment Script

echo "🚀 SkyJames Production Deployment"
echo "===================================="

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python $python_version"

# Create virtual environment
echo "📌 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate# Install dependencies
echo "📌 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install streamlit flask websockets sqlite3

# Create directories
echo "📌 Creating directories..."
mkdir -p models data/input data/output data/sports config logs

# Download model if not exists
if [ ! -f models/lane_net_optimized.pth ]; then
    echo "📌 Model not found. Please train or download model."
fi

# Set permissions
echo "📌 Setting permissions..."
chmod +x skyjames.py
chmod +x scripts/*.py

echo ""
echo "✅ SkyJames Deployment Complete!"
echo ""
echo "🚀 Run SkyJames with:"
echo "  python skyjames.py --mode webcam"
echo "  python skyjames.py --mode dashboard"
echo "  python skyjames.py --mode api"
echo "  python skyjames.py --mode stream"
echo ""
echo "📊 Start Dashboard:"
echo "  streamlit run scripts/dashboard_app.py"
echo ""
echo "🐳 Docker Build:"
echo "  docker build -t skyjames ."
echo "  docker run -it --rm skyjames --mode webcam"
