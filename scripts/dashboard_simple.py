
import streamlit as st
st.set_page_config(page_title="SkyJames", layout="wide")

st.title("🚀 SkyJames Dashboard")
st.write("Welcome to SkyJames Computer Vision Pipeline")

col1, col2, col3 = st.columns(3)
col1.metric("FPS", "26.7", "📈")
col2.metric("Model", "1.19 MB", "✅")
col3.metric("Status", "Active", "🟢")

st.subheader("Quick Links")
st.code("""
python skyjames.py --mode webcam
python skyjames.py --mode dashboard
python skyjames.py --mode api
""")
