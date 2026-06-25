#!/bin/bash
echo "🚀 Deploying SkyJames to Production"
echo "===================================="

# 1. Build Docker image
echo "📦 Building Docker image..."
docker build -t skyjames:latest .

# 2. Push to registry (if using cloud)
# docker tag skyjames:latest your-registry/skyjames:latest
# docker push your-registry/skyjames:latest

# 3. Deploy with Kubernetes
echo "☸️ Deploying to Kubernetes..."
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/skyjames -n skyjames

# 4. Set up monitoring
echo "📊 Setting up monitoring..."
kubectl apply -f k8s/monitoring.yaml

echo "✅ Production deployment complete!"
