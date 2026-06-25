#!/bin/bash
# Safe launch script for SkyJames

echo "🚀 SkyJames Safe Launch"
echo "======================="

# Check Streamlit
python -c "import streamlit; print('✅ Streamlit version:', streamlit.__version__)" || {
    echo "❌ Streamlit not working, reinstalling..."
    pip install --force-reinstall streamlit==1.28.0
}

# Run the simple dashboard
echo "📊 Launching dashboard..."
streamlit run scripts/simple_model_dashboard.py --server.port 8505
