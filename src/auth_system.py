"""
SkyJames - Professional Authentication System
"""

import hashlib
import json
import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, session
import streamlit as st

class AuthSystem:
    def __init__(self):
        self.users_file = "config/users.json"
        self.secret_key = "skyjames_super_secret_key_2024"
        self._init_users()
    
    def _init_users(self):
        """Initialize default users"""
        os.makedirs("config", exist_ok=True)
        if not os.path.exists(self.users_file):
            default_users = {
                "admin": {
                    "password": hashlib.sha256("admin123".encode()).hexdigest(),
                    "role": "admin",
                    "name": "Administrator",
                    "email": "admin@skyjames.ai"
                },
                "user": {
                    "password": hashlib.sha256("user123".encode()).hexdigest(),
                    "role": "user",
                    "name": "Demo User",
                    "email": "user@skyjames.ai"
                }
            }
            with open(self.users_file, "w") as f:
                json.dump(default_users, f, indent=2)
    
    def authenticate(self, username, password):
        """Authenticate user"""
        with open(self.users_file, "r") as f:
            users = json.load(f)
        
        if username in users:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if users[username]["password"] == hashed:
                return {
                    "username": username,
                    "role": users[username]["role"],
                    "name": users[username]["name"],
                    "email": users[username]["email"],
                    "token": jwt.encode({
                        "user": username,
                        "role": users[username]["role"],
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
                    }, self.secret_key, algorithm="HS256")
                }
        return None
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except:
            return None

def login_required(func):
    """Decorator for protected routes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = AuthSystem()
        token = request.headers.get("Authorization")
        if token:
            token = token.replace("Bearer ", "")
            payload = auth.verify_token(token)
            if payload:
                return func(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return wrapper

def create_login_page():
    """Streamlit login page"""
    st.set_page_config(page_title="SkyJames Login", layout="centered")
    
    # Custom CSS for professional login
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .login-title {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-title h1 {
            font-size: 2em;
            color: #1a1a2e;
        }
        .login-title p {
            color: #888;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
        <div class="login-title">
            <h1>🚀 SkyJames</h1>
            <p>Sign in to your account</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Sign In", type="primary", use_column_width=True):
        if username and password:
            auth = AuthSystem()
            user = auth.authenticate(username, password)
            if user:
                st.session_state.user = user
                st.session_state.authenticated = True
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        else:
            st.warning("Please enter both username and password")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
        <p>Default: admin/admin123 or user/user123</p>
    </div>
    """, unsafe_allow_html=True)
