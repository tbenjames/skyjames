#!/bin/bash
# Create demo accounts for users

python -c "
import json
import hashlib

# Load existing users
with open('config/users.json', 'r') as f:
    users = json.load(f)

# Add demo users
demo_users = {
    'demo_user1': {
        'password': hashlib.sha256('demo123'.encode()).hexdigest(),
        'role': 'user',
        'name': 'Demo User 1'
    },
    'demo_user2': {
        'password': hashlib.sha256('demo123'.encode()).hexdigest(),
        'role': 'user',
        'name': 'Demo User 2'
    }
}

users.update(demo_users)

# Save
with open('config/users.json', 'w') as f:
    json.dump(users, f, indent=2)

print('✅ Demo users created!')
print('Username: demo_user1, demo_user2')
print('Password: demo123')
"
