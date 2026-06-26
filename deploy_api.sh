#!/bin/bash
echo "Deploying SkyJames API to Cloud..."

# Option 1: Heroku
echo "Heroku:"
echo "  heroku create skyjames-api"
echo "  git push heroku main"

# Option 2: Railway
echo "Railway:"
echo "  railway login"
echo "  railway deploy"

# Option 3: Fly.io
echo "Fly.io:"
echo "  flyctl launch"
echo "  flyctl deploy"
