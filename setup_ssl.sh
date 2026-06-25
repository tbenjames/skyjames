#!/bin/bash
echo "🔒 Setting up SSL certificates..."
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
echo "✅ SSL certificates created"
