#!/bin/bash
# SkyJames Complete Enterprise Setup

echo "🚀 SkyJames Enterprise Setup"
echo "============================="

# 1. Install enterprise dependencies
echo "📦 Installing enterprise dependencies..."
pip install mlflow dvc prometheus-client python-json-logger \
    kubernetes requests flask-cors python-dotenv

# 2. Setup MLflow
echo "🔧 Setting up MLflow..."
mkdir -p mlflow_artifacts
mlflow server --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlflow_artifacts \
    --host 0.0.0.0 --port 5000 &

# 3. Setup monitoring
echo "📊 Setting up Prometheus metrics..."
mkdir -p prometheus_data

# 4. Setup data versioning
echo "📁 Setting up DVC..."
dvc init
dvc remote add -d local storage local

# 5. Create config files
mkdir -p config
cat > config/production.yaml << 'YAML'
# SkyJames Production Configuration
api:
  host: 0.0.0.0
  port: 5000
  cors_origins: ["*"]

mlflow:
  tracking_uri: "http://localhost:5000"
  experiment: "SkyJames"

monitoring:
  prometheus_port: 9090
  metrics_enabled: true

logging:
  level: INFO
  format: json
  elk_enabled: false

webhooks:
  enabled: true
  retry_count: 3

ab_testing:
  enabled: true
  traffic_split: 50
YAML

# 6. Create Docker Compose for services
cat > docker-compose.yml << 'YAML'
version: '3.8'
services:
  mlflow:
    image: mlflow/mlflow
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow_artifacts:/mlflow
    command: mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root /mlflow

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./grafana_data:/var/lib/grafana

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus_data:/prometheus

  skyjames-api:
    build: .
    ports:
      - "8000:5000"
    depends_on:
      - mlflow
      - prometheus
YAML

echo "✅ Enterprise setup complete!"
echo ""
echo "Services available:"
echo "  - MLflow: http://localhost:5000"
echo "  - Grafana: http://localhost:3000"
echo "  - Prometheus: http://localhost:9090"
echo "  - SkyJames API: http://localhost:8000"
echo ""
echo "Next steps:"
echo "  1. Run: docker-compose up -d"
echo "  2. Start training: python scripts/train_cpu.py"
echo "  3. Track experiments: mlflow ui"
