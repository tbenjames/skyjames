"""
SkyJames - Token Manager
"""

import json
import secrets
import os
from datetime import datetime

def generate_token():
    """Generate a new API token"""
    api_key = f"skyjames_api_{secrets.token_hex(24)}"
    token_info = {
        'api_key': api_key,
        'created': datetime.now().isoformat(),
        'type': 'api_access',
        'version': '2.0.0'
    }
    os.makedirs('config', exist_ok=True)
    with open('config/api_tokens.json', 'w') as f:
        json.dump(token_info, f, indent=2)
    return api_key

def get_token():
    """Get current API token"""
    try:
        with open('config/api_tokens.json', 'r') as f:
            data = json.load(f)
            return data.get('api_key')
    except:
        return None

def show_users():
    """Show user credentials"""
    try:
        with open('config/users.json', 'r') as f:
            users = json.load(f)
        print("\n📋 Users:")
        for user, data in users.items():
            print(f"  - {user}: password = {user}123")
    except:
        print("No users found")

if __name__ == "__main__":
    print("=" * 50)
    print("🔑 SkyJames Token Manager")
    print("=" * 50)
    
    # Show users
    show_users()
    
    # Generate or get token
    token = get_token()
    if token:
        print(f"\n✅ Current API Token: {token}")
        print("\n📋 How to use:")
        print(f'  curl -H "Authorization: Bearer {token}" http://localhost:5001/status')
    else:
        print("\n⚠️ No API token found. Generating new token...")
        token = generate_token()
        print(f"✅ New API Token: {token}")
    
    print("\n" + "=" * 50)
