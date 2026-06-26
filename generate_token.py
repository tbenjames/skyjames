"""
SkyJames - Generate API Token
"""

import secrets
import json
import os
from datetime import datetime

# Generate a secure API token
api_key = f"skyjames_api_{secrets.token_hex(24)}"

# Create token info
token_info = {
    'api_key': api_key,
    'created': datetime.now().isoformat(),
    'type': 'api_access',
    'version': '2.0.0',
    'users': ['admin', 'user', 'demo']
}

# Save to file
os.makedirs('config', exist_ok=True)
with open('config/api_tokens.json', 'w') as f:
    json.dump(token_info, f, indent=2)

print('=' * 60)
print('🔑 YOUR API TOKEN')
print('=' * 60)
print(f'API Key: {api_key}')
print(f'Created: {token_info["created"]}')
print(f'Type: {token_info["type"]}')
print('=' * 60)
print('')
print('📋 How to use:')
print('  curl -H "Authorization: Bearer ' + api_key + '" http://localhost:5001/status')
print('  curl -H "X-API-Key: ' + api_key + '" http://localhost:5001/status')
print('')
print('✅ Token saved to: config/api_tokens.json')
