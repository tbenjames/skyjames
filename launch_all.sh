#!/bin/bash
echo "🚀 SkyJames Production Launch"
echo "=============================="

# Start MLflow if not running
if ! curl -s http://localhost:5000 > /dev/null; then
    echo "📊 Starting MLflow..."
    mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts --host 0.0.0.0 --port 5000 &
    sleep 3
else
    echo "✅ MLflow already running"
fi

# Start Dashboard
echo "📈 Starting SkyJames Dashboard..."
streamlit run scripts/dashboard_app.py --server.port 8501

echo "✅ All services stopped"
