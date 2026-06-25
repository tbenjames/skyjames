"""
SkyJames - Analytics Dashboard (Streamlit)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="SkyJames Analytics", layout="wide")

st.title("📊 SkyJames Analytics Dashboard")

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Videos", "1,247", "+23")
with col2:
    st.metric("Total Detections", "12,456", "+345")
with col3:
    st.metric("Avg FPS", "26.7", "🟢")
with col4:
    st.metric("Uptime", "99.9%", "✅")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Video Processing Trend")
    dates = pd.date_range(end=datetime.now(), periods=30)
    values = np.random.randint(50, 200, 30)
    fig = px.line(x=dates, y=values, title="Videos Processed (30 days)")
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.subheader("🎯 Detection Accuracy")
    categories = ['Lane Detection', 'Object Detection', 'Safety Monitoring']
    values = [94.2, 87.5, 92.8]
    fig = px.bar(x=categories, y=values, title="Accuracy by Task")
    st.plotly_chart(fig, use_column_width=True)

# Recent activity
st.subheader("📋 Recent Activity")
activity_data = pd.DataFrame({
    'Time': pd.date_range(end=datetime.now(), periods=10, freq='5min'),
    'Event': ['Video Processed', 'Detection Made', 'Alert Triggered', 'Model Updated'] * 2 + ['Video Processed', 'Detection Made'],
    'Status': ['✅', '✅', '⚠️', '✅'] * 2 + ['✅', '✅']
})
st.dataframe(activity_data, use_column_width=True)

st.info("📊 Analytics dashboard is ready!")
