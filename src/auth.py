"""
SkyJames - User Authentication
"""

import hashlib
import json
import os
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self):
        self.users = {}
        self.load_users()
    
    def load_users(self):
        try:
            os.makedirs("config", exist_ok=True)
            with open("config/users.json", "r") as f:
                self.users = json.load(f)
        except:
            # Default users
            self.users = {
                "admin": {
                    "password": hashlib.sha256("admin123".encode()).hexdigest(),
                    "role": "admin"
                },
                "user": {
                    "password": hashlib.sha256("user123".encode()).hexdigest(),
                    "role": "user"
                }
            }
            self.save_users()
    
    def save_users(self):
        os.makedirs("config", exist_ok=True)
        with open("config/users.json", "w") as f:
            json.dump(self.users, f, indent=2)
    
    def login(self, username, password):
        if username in self.users:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if self.users[username]["password"] == hashed:
                return {
                    "username": username,
                    "role": self.users[username]["role"],
                    "timestamp": datetime.now().isoformat()
                }
        return None
    
    def get_users(self):
        return list(self.users.keys())

# Simple auth check function
def require_auth(func):
    def wrapper(*args, **kwargs):
        # Simple auth check - for production, use proper JWT
        return func(*args, **kwargs)
    return wrapper
