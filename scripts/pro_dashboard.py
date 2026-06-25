"""
SkyJames - Professional Dashboard with Theme Support
"""

import streamlit as st
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Theme configuration
THEMES = {
    "dark": {
        "background": "#0a0a1a",
        "card": "rgba(255,255,255,0.05)",
        "text": "#ffffff",
        "primary": "#4a6cf7",
        "secondary": "#764ba2"
    },
    "light": {
        "background": "#f5f5f7",
        "card": "white",
        "text": "#1a1a2e",
        "primary": "#4a6cf7",
        "secondary": "#764ba2"
    }
}

def apply_theme(theme_name="dark"):
    theme = THEMES.get(theme_name, THEMES["dark"])
    st.markdown(f"""
    <style>
        .stApp {{
            background: {theme["background"]} !important;
        }}
        .main-header {{
            background: {theme["card"]};
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 16px;
            color: {theme["text"]};
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .glass-card {{
            background: {theme["card"]};
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 20px;
            margin: 10px 0;
            border: 1px solid rgba(255,255,255,0.08);
        }}
    </style>
    """, unsafe_allow_html=True)

# Usage in app
def main():
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"
    
    apply_theme(st.session_state.theme)
    
    # Rest of your dashboard code...
