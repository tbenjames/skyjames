#!/bin/bash
# SkyJames Cloud Deployment Script

echo "☁️ SkyJames Cloud Deployment"
echo "============================"

# AWS Deployment
deploy_aws() {
    echo "📦 Deploying to AWS..."
    
    # Build Docker image
    docker build -t skyjames:latest .
    
    # Tag for ECR
    aws ecr create-repository --repository-name skyjames 2>/dev/null
    docker tag skyjames:latest $(aws ecr get-login-password | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/skyjames)
    docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/skyjames:latest
    
    # Deploy to ECS
    aws ecs update-service --cluster skyjames-cluster --service skyjames-service --force-new-deployment
}

# GCP Deployment
deploy_gcp() {
    echo "📦 Deploying to GCP..."
    
    # Build and push to Google Container Registry
    gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/skyjames
    
    # Deploy to Cloud Run
    gcloud run deploy skyjames \
        --image gcr.io/$(gcloud config get-value project)/skyjames \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --memory 4Gi \
        --cpu 2
}

# Azure Deployment
deploy_azure() {
    echo "📦 Deploying to Azure..."
    
    # Build and push to Azure Container Registry
    az acr build --registry skyjamesregistry --image skyjames:latest .
    
    # Deploy to Container Instances
    az container create \
        --resource-group skyjames-rg \
        --name skyjames \
        --image skyjamesregistry.azurecr.io/skyjames:latest \
        --cpu 2 \
        --memory 4 \
        --ports 5000 8501 \
        --dns-name-label skyjames
}

# DigitalOcean Deployment
deploy_digitalocean() {
    echo "📦 Deploying to DigitalOcean..."
    
    # Build and push to DigitalOcean Container Registry
    doctl registry login
    docker build -t registry.digitalocean.com/skyjames-registry/skyjames:latest .
    docker push registry.digitalocean.com/skyjames-registry/skyjames:latest
    
    # Deploy to App Platform
    doctl apps create --spec app.yaml
}

# Show menu
echo "Select cloud provider:"
echo "1) AWS (ECS)"
echo "2) GCP (Cloud Run)"  
echo "3) Azure (ACI)"
echo "4) DigitalOcean (App Platform)"
read -p "Enter choice (1-4): " choice

case $choice in
    1) deploy_aws ;;
    2) deploy_gcp ;;
    3) deploy_azure ;;
    4) deploy_digitalocean ;;
    *) echo "Invalid choice" ;;
esac
