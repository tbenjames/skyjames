"""
Simple Test Dashboard
"""

import streamlit as st

st.set_page_config(page_title="Test", layout="wide")

st.title("🚀 Test Dashboard")
st.write("If you can see this, Streamlit is working!")

if st.button("Click me"):
    st.success("✅ Button works!")

col1, col2 = st.columns(2)
with col1:
    st.info("Column 1")
with col2:
    st.success("Column 2")
