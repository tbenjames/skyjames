#!/bin/bash
echo "📦 Setting up Redis..."

# Install Redis via Docker
docker run -d \
  --name skyjames-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:alpine

echo "✅ Redis started on port 6379"
