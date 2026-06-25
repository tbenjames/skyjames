#!/bin/bash
# SkyJames DVC Setup

# Initialize DVC
dvc init

# Setup remote storage (AWS S3 example)
dvc remote add -d storage s3://skyjames-data

# Add data to DVC
dvc add data/CULane
dvc add models/lane_net_optimized.pth

# Push data to remote
dvc push

echo "✅ DVC setup complete!"
